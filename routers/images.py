# routers/images.py
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from uuid import UUID
from typing import Optional, List, Dict, Any
from utils.dependencies import get_current_user,get_current_admin_user
from services.image import create_image, get_image, get_all_images, delete_image
from services.log import record_action
from models import UserResponse 
import json

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/")
async def add_image(
    file: UploadFile = File(...),
    user_id: str = None,
    metadata: Optional[str] = None,
    # current_user: dict = Depends(get_current_user)
    current_user: UserResponse = Depends(get_current_user)  # Update type hint  
):
    try:
        metadata_dict = json.loads(metadata) if metadata else None
        image_data = await create_image(
            UUID(current_user.id),  # Update to current_user.id
            file,
            metadata_dict
        )
        # Log the action
        await record_action(
            user_id=UUID(current_user.id),  # Update to current_user.id
            action="image_upload",
            details={"image_id": str(image_data["id"])}
        )
        return image_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@router.get("/{image_id}")
async def get_image_by_id(
    image_id: UUID,
    current_user: UserResponse = Depends(get_current_user)  # Update type hint
):    
    try:
        image = await get_image(image_id)
        # Allow admins to view any image, regular users can only view their own
        if str(image["user_id"]) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized: Image does not belong to this user")
        return image
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve image: {str(e)}")

@router.get("/")
async def get_all_user_images(
    current_user: UserResponse = Depends(get_current_user)  # Update type hint
):
    try:
        # Admins can get all images (handled in admin router), regular users get their own
        return await get_all_images(UUID(current_user.id))  # Update to current_user.id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve images: {str(e)}")

@router.delete("/{image_id}")
async def delete_image_by_id(
    image_id: UUID,
    current_user: UserResponse = Depends(get_current_user)  # Update type hint
):
    try:
        image = await get_image(image_id)
        # Allow admins to delete any image, regular users can only delete their own
        if str(image["user_id"]) != str(current_user.id) and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized: Image does not belong to this user")
        await delete_image(image_id)
        # Log the action
        await record_action(
            user_id=UUID(current_user.id),  # Update to current_user.id
            action="image_delete",
            details={"image_id": str(image_id)}
        )
        return {"message": "Image deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")