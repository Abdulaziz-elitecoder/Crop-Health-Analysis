# Crop Health Analysis

## Project Purpose & Objectives
The Crop Health Analysis Using NDVI system aims to provide farmers with a powerful, AI-driven tool for real-time crop health monitoring. By utilizing advanced satellite imagery and machine learning models, the system enables farmers to assess the condition of their crops more accurately and efficiently than traditional methods. This tool allows farmers to monitor crop health based on NDVI (Normalized Difference Vegetation Index) derived from satellite images, providing real-time insights for informed decisions on irrigation, fertilization, pest control, and overall crop management.

This project is a FastAPI-based backend for a crop health classification application. It allows users to upload images (RGB or NDVI), classify them as healthy or unhealthy using a machine learning model (Inception), and manage user authentication and image storage. The backend integrates with Supabase for database and storage management.

## Documentation & Demo:

- **[Documentation]**(https://docs.google.com/document/d/1jIqdLvfqLyXKsCuHXNJP_qTE4py4X_bUegUFENE6h1w/edit?tab=t.0)
- **[Demo]**(https://drive.google.com/file/d/1c4Rwh-jMx2GhPlUnqYcXYNhhQezhOmed/view?usp=sharing)

## Features

- **User Authentication**: Sign up, sign in, and log out with email and password using Supabase Auth.
- **Image Management**: Upload, retrieve, and delete images (RGB or NDVI TIFF).
- **Image Classification**: Classify images using a pre-trained Inception model to determine crop health (healthy/unhealthy).
- **Logging**: Log API requests and errors for debugging and monitoring.
- **Secure API**: Protect endpoints with JWT-based authentication.

## Project Structure

The project is organized into the following directories and files:

- **model/**
  - `inception.keras`: Pre-trained InceptionV3 model used for NDVI-based image classification.
  - `model_script.py`: Helper utilities for loading the model and performing predictions.
  - `image_processing.py`: Core functions for preprocessing both RGB and NDVI images before feeding them into the model.
  - **notebooks/**
    - **1. MODIS Data Acquisition & Cloud Masking**: Demonstrates how to automatically fetch the MOD13QA dataset from NASA LAADS and apply cloud masking.
    - **2. Chunking & Normalization**: Shows how large 4800x4800 NDVI images are split into 500x500 chunks, how default fill values are handled, and how values are normalized to the [-1, 1] range.
    - **3. Preprocessing & Model Training**: Contains the full data preprocessing pipeline and training process for the InceptionV3 model using NDVI data .


- **routers/**
  - `auth.py`: API routes for user authentication (signup, signin, logout).
  - `users.py`: API routes for user management.
  - `images.py`: API routes for image upload, retrieval, and deletion.
  - `logs.py`: API routes for accessing request and error logs.
  - `classifications.py`: API routes for image classification and result retrieval.

- **services/**
  - `auth.py`: Business logic for user authentication.
  - `image.py`: Business logic for image handling (upload, retrieval, deletion).
  - `classification.py`: Business logic for image classification.
  - `log.py`: Business logic for logging API requests and errors.

- **utils/**
  - `crypt.py`: Utilities for password hashing and encryption.
  - `dependencies.py`: get_user_id dependency.
  - `security.py`: Security utilities for JWT token handling.

- **Root Files**
  - `config.py`: Configuration settings (e.g., Supabase URL, API keys).
  - `main.py`: Entry point for the FastAPI application.
  - `models.py`: Pydantic models for request/response validation.
  - `requirements.txt`: List of Python dependencies.
  - `api-docs.md`: Detailed API documentation, setup, and running instructions.

## Prerequisites

- Python 3.8+
- Supabase account (for database and storage)
- FastAPI and Uvicorn (installed via `requirements.txt`)
- Streamlit (installed via `requirements.txt`)
- A pre-trained Inception model (`model/inception.keras`)

## Getting Started

For detailed instructions on setting up and running the project, as well as a list of API endpoints, refer to the [API Documentation](Docs/api-docs.md).

### Quick Start

1. Clone the repository:
   ```
   git clone https://github.com/Abdulaziz-elitecoder/Crop-Health-Analysis.git
   cd into the folder
    ```
2. Create a virtual env and activate it:
    ```
    python -m venv <venv-name>

    .\<venv-name>\Scripts\activate
    ```
3. Install all requirements:
    ```
    pip install requirements.txt
    ```
4. Run FastAPI:
    ```
    uvicorn main:app --reload
    ```
5. Access the interactive docs made by swaggerUI:
    ```
    http://localhost:8000/docs
    ```
5. Run Streamlit:
    ```
    streamlit run ui.py
    ```
