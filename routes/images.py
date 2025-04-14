# routes/images.py
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from config import supabase
from models import ImageCreate, ImageResponse
from routes.auth import verify_jwt_token
from utils.security import encrypt_data, decrypt_data 

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/", response_model=ImageResponse)
async def add_image(image: ImageCreate, current_user: str = Depends(verify_jwt_token)):
    # Ensure the user_id matches the authenticated user
    if str(image.user_id) != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Encrypt the metadata before storing
    encrypted_metadata = encrypt_data(image.metadata)
    
    try:
        response = supabase.table("images").insert({
            "user_id": str(image.user_id),
            "image_url": image.image_url,
            "metadata": encrypted_metadata  # Store the encrypted metadata
        }).execute()
        # Decrypt the metadata for the response
        response_data = response.data[0]
        response_data["metadata"] = decrypt_data(response_data["metadata"])
        return response_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: UUID, current_user: str = Depends(verify_jwt_token)):
    response = supabase.table("images").select("*").eq("id", str(image_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Check if the user has access to this image
    if str(response.data[0]["user_id"]) != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Decrypt the metadata before returning
    response_data = response.data[0]
    response_data["metadata"] = decrypt_data(response_data["metadata"])
    return response_data

@router.get("/", response_model=List[ImageResponse])
async def get_all_images(current_user: str = Depends(verify_jwt_token)):
    response = supabase.table("images").select("*").eq("user_id", current_user).execute()
    
    # Decrypt the metadata for each image in the response
    for item in response.data:
        item["metadata"] = decrypt_data(item["metadata"])
    return response.data

@router.delete("/{image_id}")
async def delete_image(image_id: UUID, current_user: str = Depends(verify_jwt_token)):
    response = supabase.table("images").select("*").eq("id", str(image_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Image not found")
    if str(response.data[0]["user_id"]) != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized")
    supabase.table("images").delete().eq("id", str(image_id)).execute()
    return {"message": "Image deleted"}