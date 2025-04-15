# services/image.py
from uuid import UUID
from database.supabase import get_supabase
from typing import List, Dict, Any
from fastapi import UploadFile

async def create_image(user_id: UUID, file: UploadFile, metadata: Dict[str, Any] = None) -> dict:
    print(f"Creating image for user_id: {user_id}")

    # Validate file type
    allowed_types = ["image/tiff", "image/jpeg", "image/png", "application/octet-stream"]
    print(f"Uploaded file content-type: {file.content_type}")
    if file.content_type not in allowed_types:
        raise ValueError(f"Unsupported file type: {file.content_type}. Allowed types: {allowed_types}")
    
    # Determine file_type (rgb or ndvi)
    file_type = "rgb"
    if file.content_type == "image/tiff":
        # For TIFF files, assume NDVI unless metadata indicates otherwise
        file_type = "ndvi"  # Default to NDVI for TIFF
        if metadata and metadata.get("is_rgb", False):
            file_type = "rgb"
    print(f"Assigned file_type: {file_type}")
    
    # Read the file contents into bytes
    file_contents = await file.read()
    
    # Initialize the Supabase client with service role key
    supabase = await get_supabase()
    
    # Create a storage bucket instance
    storage_bucket = supabase.storage.from_("images")
    
    # Upload the file to Supabase Storage
    file_path = f"{user_id}/{file.filename}"
    print("Uploading file to Supabase Storage...")
    try:
        upload_response = await storage_bucket.upload(file_path, file_contents, file_options={"content-type": file.content_type})
        print(f"Upload response: {upload_response}")
    except Exception as e:
        print(f"Storage upload failed: {str(e)}")
        raise ValueError(f"Storage upload failed: {str(e)}")
    
    # Get the public URL of the uploaded file
    image_url = await storage_bucket.get_public_url(file_path)
    print(f"Public URL: {image_url}")
    
    # Insert the image record into the database
    insert_payload = {
        "user_id": str(user_id),
        "image_url": image_url,
        "metadata": metadata if metadata else {},
        "file_type": file_type  # Add file_type to the database
    }
    print(f"Inserting into images table with payload: {insert_payload}")

    try:
        response = await supabase.table("images").insert(insert_payload).execute()
        print(f"Database insert response: {response}")
    except Exception as e:
        print(f"Database insert failed: {str(e)}")
        raise ValueError(f"Database insert failed: {str(e)}")
    
    if not response.data:
        raise ValueError("Failed to store image metadata in database")
    
    return response.data[0]

async def get_image(image_id: UUID) -> dict:
    supabase = await get_supabase()
    response = await supabase.table("images").select("*").eq("id", str(image_id)).limit(1).execute()
    if not response.data:
        raise ValueError("Image not found")
    return response.data[0]

async def get_all_images(user_id: UUID) -> List[dict]:
    supabase = await get_supabase()
    response = await supabase.table("images").select("*").eq("user_id", str(user_id)).execute()
    return response.data

async def delete_image(image_id: UUID) -> None:
    supabase = await get_supabase()
    response = await supabase.table("images").select("*").eq("id", str(image_id)).execute()
    if not response.data:
        raise ValueError("Image not found")
    
    image_data = response.data[0]
    file_path = image_data["image_url"].split("images/")[-1]
    await supabase.storage.from_("images").remove([file_path])
    
    await supabase.table("images").delete().eq("id", str(image_id)).execute()

async def view_images(user_id: UUID) -> List[dict]:
    return await get_all_images(user_id)