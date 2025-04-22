# dependencies.py
from fastapi import HTTPException,Depends,status
from uuid import UUID
from models import UserResponse
from database.supabase import get_supabase


async def get_current_user(user_id: str = None) -> UserResponse:
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not provided")
    supabase = await get_supabase()
    try:
        user_response = await supabase.table("users").select("*").eq("auth_user_id", user_id).execute()
        if not user_response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user_data = user_response.data[0]
        return UserResponse(
            id=user_data["id"],
            auth_user_id=user_data["auth_user_id"],
            email=user_data["email"],
            created_at=user_data["created_at"],
            is_admin=user_data.get("is_admin", False)
        )
        # return {"user_id": str(UUID(user_id))}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    
async def get_current_admin_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """
    Ensure the current user is an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return current_user