import numpy as np
import cv2
import rasterio
import tempfile
import os
import matplotlib.pyplot as plt
from rasterio.crs import CRS
from shapely.geometry import box, mapping
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
import folium

def rgb_to_vari(img):
    """Calculate VARI from RGB image."""
    r = img[:, :, 0].astype(np.float32)
    g = img[:, :, 1].astype(np.float32)
    b = img[:, :, 2].astype(np.float32)

    denominator = r + g - b
    denominator[denominator == 0] = 1e-10  # Avoid division by zero

    vari = (g - r) / denominator
    return np.clip(vari, -1, 1)

ndvi_legend = LinearColormap(
    colors=['#d73027', '#fee08b', '#ffffbf', '#d9ef8b', '#1a9850'],
    vmin=-1, vmax=1,
    caption='NDVI value'
)

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
    
def plot_ndvi_overlay(tiff_path, zoom=14):
    try:
        with rasterio.open(tiff_path) as src:
            ndvi = src.read(1).astype(np.float32)
            bounds = src.bounds

        norm_ndvi = (ndvi + 1) / 2
        cmap = plt.get_cmap('RdYlGn')
        rgba = cmap(norm_ndvi)
        rgb = (rgba[..., :3] * 255).astype(np.uint8)

        center_lat = (bounds.bottom + bounds.top) / 2
        center_lon = (bounds.left + bounds.right) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri World Imagery'
        )

        folium.raster_layers.ImageOverlay(
            image=rgb,
            bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
            opacity=0.6
        ).add_to(m)

        ndvi_legend.add_to(m)
        return m
    except Exception as e:
        print(f"Geospatial visualization error: {e}")
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

