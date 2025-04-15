# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from uuid import UUID
from services.image import view_images
from utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/images", response_model=List[Dict])
async def get_user_images(current_user: dict = Depends(get_current_user)):
    try:
        user_id = UUID(current_user["user_id"])
        images = await view_images(user_id)
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve images: {str(e)}")