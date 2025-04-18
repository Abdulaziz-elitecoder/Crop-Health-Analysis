# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for rasterio, opencv, and other libraries
RUN apt-get update && apt-get install -y \
    libgeos-dev \
    libgdal-dev \
    libatlas-base-dev \
    gfortran \
    libjpeg-dev \
    zlib1g-dev \
    libglib2.0-0 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Git LFS
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
    && apt-get install -y git-lfs \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository and fetch Git LFS files
RUN git clone https://github.com/Abdulaziz-elitecoder/Crop-Health-Analysis.git /tmp/repo \
    && cd /tmp/repo \
    && git lfs install \
    && git lfs pull \
    && mv /tmp/repo/* /app/ \
    && rm -rf /tmp/repo

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r backend-requirements.txt
# Debug: List the contents of the model/ directory to verify the file is present
RUN ls -la model/

# Expose the port for FastAPI
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]