import numpy as np
import requests
from PIL import Image
from io import BytesIO
from uuid import UUID
from typing import Dict
from database.supabase import get_supabase
from services.image import get_image
from model.image_processing import preprocess_image, preprocess_ndvi
from model.model_script import load_model,predict
from fastapi import UploadFile

# Global variable to store the loaded model
_model = None
CLASS_NAMES = ['Non-Plant', 'Unhealthy', 'Moderate', 'Healthy']

def load_model_wrapper():
    """
    Load the machine learning model for image classification.
    """
    global _model
    try:
        model_path = "model/Inception.keras"
        print(f"Loading model from: {model_path}")
        _model = load_model(model_path=model_path)
        print("Model loaded successfully")
        return _model
    except FileNotFoundError as e:
        raise RuntimeError(f"Model file not found at {model_path}: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {str(e)}")

async def classify_image(image_id: UUID, user_id: UUID) -> Dict:
    global _model
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")

    # Verify the image exists and belongs to the user
    image = await get_image(image_id)
    if str(image["user_id"]) != str(user_id):
        raise ValueError("Unauthorized: Image does not belong to this user")

    # Get the file type from the database
    file_type = image.get("file_type", "rgb")  # Default to rgb if not specified
    print(f"Image file type from database: {file_type}")

    # Download the image from the image_url
    image_url = image["image_url"]
    print(f"Attempting to classify image from URL: {image_url}")

    try:
        headers = {}

        print("Sending HTTP GET request to download the image...")
        response = requests.get(image_url, headers=headers)
        print(f"HTTP Status Code: {response.status_code}")
        response.raise_for_status() 

        content_type = response.headers.get("content-type", "unknown")
        content_length = response.headers.get("content-length", "unknown")
        print(f"Content-Type: {content_type}")
        print(f"Content-Length: {content_length} bytes")

        if not content_type.startswith("image/"):
            raise ValueError(f"URL does not point to an image. Content-Type: {content_type}")

        if file_type == "rgb" and content_type == "image/tiff":
            print("Detected TIFF image, but file_type is rgb. Switching to ndvi processing as fallback...")
            file_type = "ndvi" 

        # Get the content
        content = response.content
        print(f"Downloaded content size: {len(content)} bytes")

        # Verify the downloaded size matches the expected size
        if content_length != "unknown" and len(content) != int(content_length):
            raise ValueError(f"Downloaded content size ({len(content)}) does not match Content-Length ({content_length})")

        # Log the first few bytes of the content to inspect it
        first_bytes = content[:10]
        print(f"First 10 bytes of content: {first_bytes}")

        # Check if the content is empty
        if not content:
            raise ValueError("Downloaded content is empty")

        # Process the image based on file_type
        if file_type == "rgb":
            print("Processing image as RGB...")
            try:
                print("Attempting to open image with PIL...")
                img = Image.open(BytesIO(content))
                print("Image opened successfully with PIL")

                # Convert to RGB if necessary
                if img.mode != "RGB":
                    print(f"Converting image mode from {img.mode} to RGB")
                    img = img.convert("RGB")
                img_rgb = np.array(img)
                print("Image converted to NumPy array successfully")

                # Preprocess as RGB image using image_processing.py
                print("Preprocessing RGB image...")
                processed_data = preprocess_image(img_rgb)
                print("RGB image preprocessed successfully")
            except Exception as e:
                raise ValueError(f"Failed to process RGB image: {str(e)}")

        elif file_type == "ndvi":
            print("Processing image as NDVI...")
            try:
                # Create a fake UploadFile for preprocess_ndvi
                filename = "temp.tiff" if content_type == "image/tiff" else "temp.npy"
                uploaded_file = UploadFile(filename=filename, file=BytesIO(content))
                print("Preprocessing NDVI image...")
                processed_data = await preprocess_ndvi(uploaded_file)
                print("NDVI image preprocessed successfully")
            except Exception as e:
                raise ValueError(f"Failed to process NDVI image: {str(e)}")

        else:
            raise ValueError(f"Unsupported file_type: {file_type}")

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to download image: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")

    # Make a prediction using model_script.py
    print("Making prediction with the model...")
    try:
        class_idx, confidence = predict(_model, processed_data)
        print(f"Prediction successful: class_idx={class_idx}, confidence={confidence}")
    except Exception as e:
        raise ValueError(f"Prediction failed: {str(e)}")

    classification = CLASS_NAMES[class_idx]
    print(f"Mapped class_idx to classification: {classification}")

    # Insert the classification into the database
    print("Inserting classification into the database...")
    supabase = await get_supabase()
    insert_payload = {
        "image_id": str(image_id),
        "classification": classification,
        "confidence": confidence
    }
    response = await supabase.table("classifications").insert(insert_payload).execute()
    if not response.data:
        raise ValueError("Failed to store classification in database")
    print("Classification stored in database successfully")

    return response.data[0]

async def get_result(image_id: UUID, user_id: UUID) -> Dict:
    supabase = await get_supabase()
    
    # Verify the image belongs to the user
    image = await get_image(image_id)
    if str(image["user_id"]) != str(user_id):
        raise ValueError("Unauthorized: Image does not belong to this user")

    # Retrieve the latest classification for the image
    response = await supabase.table("classifications").select("*").eq("image_id", str(image_id)).order("created_at", desc=True).limit(1).execute()
    if not response.data:
        raise ValueError("No classification found for this image")

    return response.data[0]