# utils/image_processing.py
import numpy as np
import cv2
import rasterio
import tempfile
import tensorflow as tf

def rgb_to_vari(img):
    """Calculate VARI from RGB image"""
    r = img[:,:,0].astype(np.float32)
    g = img[:,:,1].astype(np.float32)
    b = img[:,:,2].astype(np.float32)
    
    denominator = r + g - b
    denominator[denominator == 0] = 1e-10  # Avoid division by zero
    
    vari = (g - r) / denominator
    return np.clip(vari, -1, 1)  # Ensure valid range

def preprocess_image(img_rgb):
    """Process RGB images to match model input requirements"""
    # Convert to VARI and resize
    vari = rgb_to_vari(img_rgb)
    resized = cv2.resize(vari, (299, 299))
    
    # Stack to 3 channels
    return np.stack([resized]*3, axis=-1)

def preprocess_ndvi(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    try:
        if uploaded_file.name.lower().endswith('.npy'):
            ndvi = np.load(tmp_file_path)
        elif uploaded_file.name.lower().endswith(('.tif', '.tiff')):
            with rasterio.open(tmp_file_path) as src:
                ndvi = src.read(1).astype(np.float32)
        
        # Preserve original values except NaNs
        valid_mean = np.nanmean(ndvi)
        processed = np.where(np.isnan(ndvi), valid_mean, ndvi)
        
        # Maintain original NDVI range [-1, 1]
        processed = np.clip(processed, -1, 1)
        resized = cv2.resize(processed, (299, 299))
        
        return np.stack([resized]*3, axis=-1)

    finally:
        import os
        os.unlink(tmp_file_path)