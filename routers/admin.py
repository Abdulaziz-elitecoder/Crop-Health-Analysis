from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from database.supabase import get_supabase
from models import UserResponse, ImageResponse, ImageCreate,UserSignUp
from routers.auth import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

# Existing endpoint to get all images (not modified, included for context)
@router.get("/images", response_model=List[ImageResponse])
async def get_all_images(current_user: UserResponse = Depends(get_current_admin_user)):
    """
    Get all images and their associated users.
    """
    supabase = get_supabase()
    try:
        # Fetch all images
        images_response = supabase.table("images").select("*").execute()
        if not images_response.data:
            return []

        images = [
            ImageResponse(
                id=image["id"],
                user_id=image["user_id"],
                image_url=image["image_url"],
                metadata=image["metadata"],
                created_at=image["created_at"]
            )
            for image in images_response.data
        ]
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch images: {str(e)}")

# Endpoint to get all users (already implemented)
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(current_user: UserResponse = Depends(get_current_admin_user)):
    """
    Get all users.
    """
    supabase = get_supabase()
    try:
        users_response = supabase.table("users").select("*").execute()
        if not users_response.data:
            return []

        users = [
            UserResponse(
                id=user["id"],
                auth_user_id=user["auth_user_id"],
                email=user["email"],
                created_at=user["created_at"],
                is_admin=user.get("is_admin", False)
            )
            for user in users_response.data
        ]
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

# Existing endpoint to create an image (not modified, included for context)
@router.post("/images", response_model=ImageResponse)
async def create_image(image: ImageCreate, current_user: UserResponse = Depends(get_current_admin_user)):
    """
    Create a new image (admin only).
    """
    supabase = get_supabase()
    try:
        # For simplicity, we'll assume the image is already uploaded to Supabase Storage
        # and we're just creating a record in the images table.
        # In a real scenario, you'd upload the image file and get its URL.
        image_data = {
            "user_id": str(current_user.id),  # Assign to the admin user
            "image_url": "https://placeholder-url.com/image.jpg",  # Placeholder URL
            "metadata": image.metadata
        }
        response = supabase.table("images").insert(image_data).execute()
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create image")

        image_record = response.data[0]
        return ImageResponse(
            id=image_record["id"],
            user_id=image_record["user_id"],
            image_url=image_record["image_url"],
            metadata=image_record["metadata"],
            created_at=image_record["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create image: {str(e)}")

# Existing endpoint to delete an image (not modified, included for context)
@router.delete("/images/{image_id}")
async def delete_image(image_id: str, current_user: UserResponse = Depends(get_current_admin_user)):
    """
    Delete an image by ID (admin only).
    """
    supabase = get_supabase()
    try:
        # Check if the image exists
        image_response = supabase.table("images").select("*").eq("id", image_id).execute()
        if not image_response.data:
            raise HTTPException(status_code=404, detail="Image not found")

        # Delete the image record
        supabase.table("images").delete().eq("id", image_id).execute()
        return {"message": f"Image {image_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")

# Existing endpoint to create a user (not modified, included for context)
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserSignUp, current_user: UserResponse = Depends(get_current_admin_user)):
    """
    Create a new user (admin only).
    """
    supabase = get_supabase()
    try:
        # Sign up user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
        })
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="User creation failed")

        # Store user in users table
        user_data = {
            "auth_user_id": auth_response.user.id,
            "email": user.email,
            "is_admin": False  # New users created by admin are not admins by default
        }
        response = supabase.table("users").insert(user_data).execute()
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create user in database")

        user_record = response.data[0]
        return UserResponse(
            id=user_record["id"],
            auth_user_id=user_record["auth_user_id"],
            email=user_record["email"],
            created_at=user_record["created_at"],
            is_admin=user_record.get("is_admin", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

# Endpoint to delete any user (already implemented)
@router.delete("/users/{user_id}")
async def delete_user(user_id: UUID, current_user: UserResponse = Depends(get_current_admin_user)):
    """
    Delete a user by ID (admin only).
    """
    supabase = get_supabase()
    try:
        # Check if the user exists
        user_response = supabase.table("users").select("*").eq("id", str(user_id)).execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")

        user = user_response.data[0]
        auth_user_id = user["auth_user_id"]

        # Delete the user from the users table
        supabase.table("users").delete().eq("id", str(user_id)).execute()

        # Delete the user from Supabase Auth (requires admin privileges in Supabase)
        supabase.auth.admin.delete_user(auth_user_id)

        return {"message": f"User {user_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")