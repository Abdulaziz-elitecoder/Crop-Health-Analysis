# main.py
from fastapi import FastAPI
from routes import users, images, classifications, auth

app = FastAPI(
    title="Crop Health Analysis Backend",
    description="Backend for NDVI-based crop health monitoring",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(images.router)
app.include_router(classifications.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Crop Health Analysis Backend"}