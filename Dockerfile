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
    # libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copy the necessary backend files into the container
# COPY main.py .
# COPY routers/ routers/
# COPY services/ services/
# COPY utils/ utils/
# COPY models.py .
# COPY model/ model/
# COPY database/ database/
# COPY .env .
# COPY config.py .

# Install Git LFS
RUN apt-get update && apt-get install -y curl \
    && curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
    && apt-get install -y git-lfs \
    && rm -rf /var/lib/apt/lists/*

# Since Railway clones the repo, we need to ensure Git LFS files are fetched
# Railway builds from the repo directly, so we simulate the LFS fetch in the build context
WORKDIR /app
COPY main.py .
COPY routers/ routers/
COPY services/ services/
COPY utils/ utils/
COPY models.py .
COPY model/ model/
COPY database/ database/
COPY .env .
COPY config.py .
RUN git lfs install && git lfs pull

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r backend-requirements.txt

# Debug: List the contents of the model/ directory to verify the file is present
RUN ls -la model/

# Expose the port for FastAPI
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]