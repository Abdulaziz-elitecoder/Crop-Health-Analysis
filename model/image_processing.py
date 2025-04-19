import numpy as np
import cv2
import rasterio
import tempfile
import os
from rasterio.crs import CRS

def rgb_to_vari(img):
    """Calculate VARI from RGB image."""
    r = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    b = img[:, :, 2].astype(np.float32)

    denominator = r + g - b
    denominator[denominator == 0] = 1e-10  # Avoid division by zero

    vari = (g - r) / denominator
    return np.clip(vari, -1, 1)

def preprocess_image(img_rgb):
    """Convert RGB image to VARI, resize, and format for model."""
    vari = rgb_to_vari(img_rgb)
    resized = cv2.resize(vari, (299, 299))
    return np.stack([resized] * 3, axis=-1)

def get_geodata(file_path):
    """Extract geospatial metadata from GeoTIFF."""
    try:
        with rasterio.open(file_path) as src:
            if not src.crs or not src.bounds:
                return None  # Not a valid GeoTIFF

            bounds = src.bounds
            geojson = {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": mapping(box(bounds.left, bounds.bottom, bounds.right, bounds.top)),
                    "properties": {"CRS": str(src.crs)}
                }]
            }
            return geojson
    except Exception as e:
        print(f"Error reading geodata: {e}")
        return None

def preprocess_ndvi(input_data):
    """Process NDVI files and return processed data with geodata."""
    geo_data = None

    if isinstance(input_data, str):  # It's a file path
        file_path = input_data
        file_name = input_data.lower()
    else:  # It's an uploaded file (file-like object)
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(input_data.read())
            file_path = tmp_file.name
        file_name = input_data.name.lower()

    try:
        if file_name.endswith('.npy'):
            ndvi = np.load(file_path)
        elif file_name.endswith(('.tif', '.tiff')):
            geo_data = get_geodata(file_path)
            with rasterio.open(file_path) as src:
                ndvi = src.read(1).astype(np.float32)
        else:
            raise ValueError("Unsupported file format")

        valid_mean = np.nanmean(ndvi)
        processed = np.where(np.isnan(ndvi), valid_mean, ndvi)
        smoothed = cv2.GaussianBlur(processed, (5, 5), 0)
        resized = cv2.resize(smoothed, (299, 299))
        processed_data = np.stack([resized]*3, axis=-1)

        return processed_data, geo_data

    finally:
        if not isinstance(input_data, str):  # Clean up only if we created a temp file
            os.unlink(file_path)

