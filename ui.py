import streamlit as st
import requests
import json
import io
import os
from typing import Optional, Dict, List
from PIL import Image
import pandas as pd
import uuid
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from services.classification import load_model_wrapper , predict
from model.image_processing import preprocess_image, plot_ndvi_overlay
from streamlit_folium import folium_static
import cv2

# API endpoint configuration
API_URL = "http://localhost:8000"  

# Class names for mapping class_idx to labels
CLASS_NAMES = ['Non-Plant', 'Unhealthy', 'Moderate', 'Healthy']

# Session state management
def init_session_state():
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"
    if "images" not in st.session_state:
        st.session_state.images = []
    if "selected_image" not in st.session_state:
        st.session_state.selected_image = None
    if "video_capture" not in st.session_state:
        st.session_state.video_capture = None

def set_authenticated(user_id: str, access_token: str, refresh_token: str, email: str):
    st.session_state.user_id = user_id
    st.session_state.access_token = access_token
    st.session_state.email = email
    st.session_state.refresh_token = refresh_token
    st.session_state.is_authenticated = True
    st.session_state.current_page = "dashboard"

def clear_authentication():
    st.session_state.user_id = None
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.email = None
    st.session_state.is_authenticated = False
    st.session_state.current_page = "login"
    st.session_state.images = []
    st.session_state.selected_image = None
    if st.session_state.video_capture is not None:
        st.session_state.video_capture.release()
        st.session_state.video_capture = None

# API interaction functions
def signup_user(email: str, password: str) -> Optional[dict]:
    try:
        response = requests.post(
            f"{API_URL}/auth/signup",
            params={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Signup failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None


def signin_user(email: str, password: str) -> Optional[dict]:
    try:
        response = requests.post(
            f"{API_URL}/auth/signin",
            params={"email": email, "password": password}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def logout_user(access_token: str) -> bool:
    try:
        response = requests.post(
            f"{API_URL}/auth/logout",
            params={"access_token": access_token}
        )
        if response.status_code == 200:
            return True
        else:
            st.error(f"Logout failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False

def get_auth_headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def upload_image(file, metadata=None):
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        data = {"user_id": st.session_state.user_id}
        if metadata:
            data["metadata"] = json.dumps(metadata)
        
        response = requests.post(
            f"{API_URL}/images/?user_id={st.session_state.user_id}",
            headers=get_auth_headers(),
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error uploading image: {str(e)}")
        return None

def get_all_images():
    try:
        response = requests.get(
            f"{API_URL}/images/?user_id={st.session_state.user_id}",
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to retrieve images: {response.json().get('detail', 'Unknown error')}")
            return []
    except Exception as e:
        st.error(f"Error retrieving images: {str(e)}")
        return []

def get_image_by_id(image_id):
    try:
        response = requests.get(
            f"{API_URL}/images/{image_id}?user_id={st.session_state.user_id}",
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to retrieve image: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error retrieving image: {str(e)}")
        return None

def delete_image(image_id):
    try:
        response = requests.delete(
            f"{API_URL}/images/{image_id}?user_id={st.session_state.user_id}",
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to delete image: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error deleting image: {str(e)}")
        return False

def classify_image(image_id):
    try:
        response = requests.post(
            f"{API_URL}/classifications/{image_id}?user_id={st.session_state.user_id}",
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Classification failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error classifying image: {str(e)}")
        return None

def get_classification_result(image_id):
    try:
        response = requests.get(
            f"{API_URL}/classifications/{image_id}/result?user_id={st.session_state.user_id}",
            headers=get_auth_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error retrieving classification: {str(e)}")
        return None

# UI Components
def render_login_page():
    st.title("Crop Health Analysis")
    st.subheader("Login to your account")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        with st.form("signin_form"):
            email = st.text_input("Email", key="signin_email")
            password = st.text_input("Password", type="password", key="signin_password")
            submit_button = st.form_submit_button("Sign In")
            
            if submit_button:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    user_data = signin_user(email, password)
                    if user_data:
                        set_authenticated(
                            user_data["user_id"], 
                            user_data["access_token"],
                            user_data["refresh_token"],
                            email
                        )
                        st.rerun()
    
    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_button = st.form_submit_button("Sign Up")
            
            if submit_button:
                if not email or not password or not confirm_password:
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    user_data = signup_user(email, password)
                    if user_data:
                        st.success("Account created successfully! You can now sign in.")
                        set_authenticated(
                            user_data["user_id"], 
                            user_data["access_token"],
                            user_data["refresh_token"],
                            email
                        )
                        st.rerun()

def render_dashboard():
    st.title("Crop Health Analysis Dashboard")
    
    # Sidebar navigation
    with st.sidebar:
        st.subheader("Navigation")
        page = st.radio("Go to", ["Upload Image", "My Images", "Account" , "Live Webcam Classification","Live Feed Capture"])
        
        st.divider()
        if st.button("Logout"):
            if logout_user(st.session_state.access_token):
                clear_authentication()
                st.rerun()
    
    # Main content based on selected page
    if page == "Upload Image":
        render_upload_page()
    elif page == "My Images":
        render_images_page()
    elif page == "Account":
        render_account_page()
    elif page == "Live Webcam Classification":
        render_webcam_page()
    elif page == "Live Feed Capture":
        render_live_feed_page()

def render_upload_page():
    st.header("Upload New Image")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png", "tif", "tiff","npy"])
    
    # Metadata form
    with st.expander("Image Metadata (Optional)"):
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location")
            crop_type = st.text_input("Crop Type")
    
    # Image type selection
    image_type = st.radio("Image Type", ["RGB", "NDVI"], horizontal=True)
    
    if uploaded_file is not None:
        # Preview the uploaded file based on its type
        file_extension = uploaded_file.name.lower().split('.')[-1]
        if file_extension in ["jpg", "jpeg", "png"]:
            # Display JPEG/PNG images directly
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image (RGB)", use_container_width=True)
        elif file_extension in ["tif", "tiff"]:
            # Display TIFF files (NDVI or RGB)
            with io.BytesIO(uploaded_file.getvalue()) as f:
                with rasterio.open(f) as src:
                    data = src.read()
            if data.shape[0] in [3, 4]:  # RGB or RGBA
                # Convert to (height, width, channels) for display
                rgb_data = data[:3].transpose(1, 2, 0)  # Take first 3 bands
                fig, ax = plt.subplots()
                ax.imshow(rgb_data)
                ax.set_title("Uploaded Image (RGB TIFF)")
                ax.axis('off')
                st.pyplot(fig)
            else:
                # Assume single-band NDVI
                ndvi_display = data[0, :, :] if data.ndim == 3 else data[:, :]
                fig, ax = plt.subplots()
                im = ax.imshow(ndvi_display, cmap='RdYlGn', vmin=-1, vmax=1)
                plt.colorbar(im, label="NDVI")
                ax.set_title("Uploaded Image (NDVI TIFF)")
                st.pyplot(fig)
        elif file_extension == "npy":
            # Display NPY files (NDVI data)
            with io.BytesIO(uploaded_file.getvalue()) as f:
                ndvi_data = np.load(f)
            # Ensure the data is 2D (height, width)
            if ndvi_data.ndim > 2:
                ndvi_data = ndvi_data[0, :, :] if ndvi_data.shape[0] == 1 else ndvi_data[:, :, 0]
            fig, ax = plt.subplots()
            im = ax.imshow(ndvi_data, cmap='RdYlGn', vmin=-1, vmax=1)
            plt.colorbar(im, label="NDVI")
            ax.set_title("Uploaded Image (NDVI NPY)")
            st.pyplot(fig)
        else:
            st.warning(f"Cannot preview file format: {file_extension}")
            
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Upload button
        if st.button("Upload Image"):
            # Prepare metadata
            metadata = {
                "location": location,
                "crop_type": crop_type,
                "image_type": image_type.lower()
            }
            
            # Upload image
            with st.spinner("Uploading..."):
                result = upload_image(uploaded_file, metadata)
                if result:
                    st.success("Image uploaded successfully!")
                    st.json(result)
                    # Refresh images list
                    st.session_state.images = get_all_images()

def render_images_page():
    st.header("My Images")
    
    # Refresh button
    if st.button("Refresh Images"):
        st.session_state.images = get_all_images()
    
    # Get images if not already loaded
    if not st.session_state.images:
        with st.spinner("Loading images..."):
            st.session_state.images = get_all_images()
    
    # Display images
    if not st.session_state.images:
        st.info("No images found. Upload some images first!")
    else:
        # Create a dataframe for better display
        image_data = []
        for img in st.session_state.images:
            # Extract metadata
            metadata = img.get("metadata", {})
            image_data.append({
                "ID": img["id"],
                "Type": img.get("file_type", "Unknown"),
                "Location": metadata.get("location", ""),
                "Uploaded": img.get("created_at", "")[:10]  # Just the date part
            })
        
        # Convert to dataframe
        df = pd.DataFrame(image_data)
        
        # Use AgGrid or similar for better interaction if available
        st.dataframe(df, use_container_width=True, height=300)
        
        # Image selection
        selected_id = st.selectbox("Select an image to view details", 
                                  options=[img["id"] for img in st.session_state.images],
                                  format_func=lambda x: f"Image {x[:8]}...")
        
        if selected_id:
            # Find the selected image
            selected_image = next((img for img in st.session_state.images if img["id"] == selected_id), None)
            if selected_image:
                st.session_state.selected_image = selected_image
                
                # Display image details
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Image Preview")
                    try:
                        # Download the image content
                        image_url = selected_image["image_url"]
                        file_type = selected_image.get("file_type", "rgb")
                        image_response = requests.get(image_url)
                        if image_response.status_code == 200:
                            image_content = image_response.content
                            
                            # Get classification result for the title
                            classification = get_classification_result(selected_id)
                            title = "Image Preview"
                            if classification:
                                result = classification["classification"]
                                confidence = classification["confidence"]
                                title = f"{result} ({confidence:.1%})"
                            
                            # Display based on file_type
                            if file_type == "ndvi":
                                # NDVI image (TIFF)
                                with io.BytesIO(image_content) as f:
                                    m = plot_ndvi_overlay(f)
                                    with rasterio.open(f) as src:
                                        data = src.read()  # Shape: (bands, height, width)
                                ndvi_display = data[0, :, :] if data.ndim == 3 else data[:, :]
                                fig, ax = plt.subplots()
                                im = ax.imshow(ndvi_display, cmap='RdYlGn', vmin=-1, vmax=1)
                                plt.colorbar(im, label="NDVI")
                                ax.set_title(title)
                                st.pyplot(fig)
                                with io.BytesIO(image_content) as f:
                                    m = plot_ndvi_overlay(f)
                                    if m:
                                        st.subheader("Geospatial Visualization")
                                        folium_static(m)
                            else:
                                # RGB image (JPEG/PNG)
                                image = Image.open(io.BytesIO(image_content))
                                fig, ax = plt.subplots()
                                ax.imshow(np.array(image))
                                ax.set_title(title)
                                ax.axis('off')
                                st.pyplot(fig)
                        else:
                            st.warning(f"Failed to download image: {image_response.status_code}")
                    except Exception as e:
                        st.warning(f"Cannot preview this image: {str(e)}")
                
                with col2:
                    st.subheader("Image Details")
                    metadata = selected_image.get("metadata", {})
                    st.write(f"**Type:** {selected_image.get('file_type', 'Unknown')}")
                    st.write(f"**Location:** {metadata.get('location', 'Not specified')}")
                    st.write(f"**Date:** {metadata.get('capture_date', 'Not specified')}")
                    
                    # Classification section
                    st.divider()
                    st.subheader("Classification")
                    
                    # Check if classification exists
                    classification = get_classification_result(selected_id)
                    
                    if classification:
                        # Display classification result
                        result = classification["classification"]
                        confidence = classification["confidence"]
                        
                        # Color based on health status
                        if (result != "Unhealthy" or result != "Non-Plant"):
                            st.success(f"Status: {result} (Confidence: {confidence:.2f})")
                        else:
                            st.error(f"Status: {result} (Confidence: {confidence:.2f})")
                        
                        st.write(f"Classified on: {classification['created_at'][:10]}")
                    else:
                        st.info("This image has not been classified yet.")
                        if st.button("Classify Image"):
                            with st.spinner("Classifying..."):
                                result = classify_image(selected_id)
                                if result:
                                    st.success("Classification complete!")
                                    st.rerun()
                
                # Actions
                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Delete Image"):
                        if delete_image(selected_id):
                            st.success("Image deleted successfully!")
                            # Refresh images list
                            st.session_state.images = get_all_images()
                            st.session_state.selected_image = None
                            st.rerun()

def render_webcam_page():
    st.header("Live Webcam Classification")
    camera_image = st.camera_input("Take a picture using your webcam")
    
    if camera_image:
        try:
            img = Image.open(camera_image)
            img_rgb = np.array(img)
            data = preprocess_image(img_rgb)
    
            model = load_model_wrapper()
            class_idx, confidence = predict(model, data)
    
            col1, col2 = st.columns(2)
            with col1:
                st.image(img_rgb, caption='Captured Image', use_container_width=True)
                st.write(f"Predicted: {CLASS_NAMES[class_idx]} ({confidence:.1%})")

            with col2:
                fig, ax = plt.subplots()
                ndvi_display = data[0, :, :, 0] if data.ndim == 4 else data[:, :, 0]
                ax.imshow(ndvi_display, cmap='RdYlGn', vmin=-1, vmax=1)
                ax.set_title(f"{CLASS_NAMES[class_idx]} ({confidence:.1%})")
                ax.axis('off')
                st.pyplot(fig)
    
        except Exception as e:
            st.error(f"Error processing webcam image: {e}")


def ndvi_calculation(bgr_frame):
    """
    Approximate an NDVI-like index from a BGR webcam frame
    using green and red channels as a proxy.
    """
    frame_rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
    # Extract red and green channels
    red = frame_rgb[:, :, 0].astype(np.float32)
    green = frame_rgb[:, :, 1].astype(np.float32)
    # Compute pseudo-NDVI: (green - red) / (green + red)
    denominator = green + red + 1e-8  # Avoid division by zero
    ndvi = (green - red) / denominator
    # Clamp to [-1, 1] to ensure valid NDVI range
    ndvi = np.clip(ndvi, -1.0, 1.0)
    return ndvi

def predict_image(model, data: np.ndarray) -> tuple:
    """
    Predict the class and confidence for the input data.
    Expects data in [0, 1] with shape (299, 299, 3).
    """
    # Add batch dimension
    data = np.expand_dims(data, axis=0)  # Shape: (1, 299, 299, 3)
    # If model expects [-1, 1], uncomment the following:
    # data = (data * 2.0) - 1.0
    # Run prediction
    predictions = model.predict(data)
    class_idx = np.argmax(predictions[0])
    confidence = predictions[0][class_idx]
    return CLASS_NAMES[class_idx], confidence

def preprocess_for_model(ndvi):
    """
    Resize, replace NaNs, normalize to [0,1],
    and stack into 3 channels for Inception
    """
    TARGET_SIZE = (299, 299)  # (height, width)
    resized = cv2.resize(ndvi, TARGET_SIZE)
    # Replace NaNs with a safe value (e.g., -2, outside typical NDVI range)
    safe = np.nan_to_num(resized, nan=-2)
    # Normalize to [0, 1]
    norm = (safe - safe.min()) / (safe.max() - safe.min() + 1e-8)
    # Explicitly clamp to [0, 1] to avoid numerical issues
    norm = np.clip(norm, 0.0, 1.0)
    # Stack into 3 channels
    stacked = np.stack([norm, norm, norm], axis=-1).astype(np.float32)
    return stacked

def render_live_feed_page():
    st.header("Live Feed Capture")
    
    # Initialize video capture if not already done
    if st.session_state.video_capture is None:
        st.session_state.video_capture = cv2.VideoCapture(0)
        if not st.session_state.video_capture.isOpened():
            st.error("Could not open webcam. Please ensure a webcam is connected and accessible.")
            st.session_state.video_capture = None
            return
    
    st.write("Click the button below to capture and classify a frame from the webcam.")
    
    # Button to capture and process a frame
    if st.button("Capture Frame"):
        try:
            # Read frame from webcam
            ret, frame = st.session_state.video_capture.read()
            if not ret:
                st.error("Frame capture failed. Please try again or check your webcam.")
                return
            
            # Crop to square for consistency
            h, w = frame.shape[:2]
            m = min(h, w)
            frame_sq = frame[(h-m)//2:(h+m)//2, (w-m)//2:(w+m)//2]
            
            # Calculate NDVI
            ndvi = ndvi_calculation(frame_sq)
            # Preprocess for model
            processed = preprocess_for_model(ndvi)
            # Load model and predict
            model = load_model_wrapper()
            label, conf = predict(model, processed)
            
            # Choose text color by label
            colors = {
                'Non-Plant': (0, 0, 255),  # Red
                'Unhealthy': (0, 165, 255),  # Orange
                'Moderate': (255, 255, 0),  # Yellow
                'Healthy': (0, 255, 0)  # Green
            }
            color = colors.get(label, (255, 255, 255))  # Default to white
            
            # Overlay label and confidence on original frame_sq (not processed)
            frame_display = frame_sq.copy()  # Work on a copy to preserve original
            text = f"{CLASS_NAMES[label]}: ({conf*100:.0f}%)"
            cv2.putText(frame_display, text, (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Convert frame to RGB for Streamlit display (OpenCV uses BGR)
            frame_rgb = cv2.cvtColor(frame_display, cv2.COLOR_BGR2RGB)
            
            # Display the frame
            st.image(frame_rgb, caption="Captured Frame", use_container_width=True)
            
            # Optionally display NDVI visualization
            st.subheader("NDVI Visualization")
            fig, ax = plt.subplots()
            im = ax.imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
            plt.colorbar(im, label="NDVI")
            ax.set_title("Pseudo-NDVI")
            ax.axis('off')
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error processing live feed frame: {str(e)}")
    
    # Button to stop the live feed
    if st.button("Stop Webcam"):
        if st.session_state.video_capture is not None:
            st.session_state.video_capture.release()
            st.session_state.video_capture = None
            st.success("Webcam stopped.")
            st.rerun()


def render_account_page():
    st.header("Account Information")
    
    # Display user info
    st.subheader("User Details")
    st.write(f"**User ID:** {st.session_state.user_id}")
    st.write(f"**Email:** {st.session_state.email}")
    
    # Token information in an expander
    with st.expander("Session Information"):
        st.json({
            "user_id": st.session_state.user_id,
            "access_token": st.session_state.access_token[:20] + "..." if st.session_state.access_token else None,
            "is_authenticated": st.session_state.is_authenticated
        })
    
    # Usage statistics
    st.subheader("Usage Statistics")
    image_count = len(st.session_state.images) if st.session_state.images else 0
    st.metric("Total Images", image_count)
    
    # Account actions
    st.divider()
    st.subheader("Account Actions")
    if st.button("Logout", key="account_logout"):
        if logout_user(st.session_state.access_token):
            clear_authentication()
            st.rerun()

# Main app
def main():
    st.set_page_config(
        page_title="Crop Health Analysis", 
        page_icon="🌱", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Render appropriate page based on authentication status
    if st.session_state.is_authenticated:
        render_dashboard()
    else:
        render_login_page()

if __name__ == "__main__":
    main()