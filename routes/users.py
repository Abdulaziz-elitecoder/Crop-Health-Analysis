# routes/users.py
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from config import supabase
from models import UserCreate, UserResponse
from routes.auth import verify_jwt_token

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
async def add_user(user: UserCreate, current_user: str = Depends(verify_jwt_token)):
    # Only allow admin users to add users (you can implement admin checks)
    try:
        response = supabase.table("users").insert({
            "email": user.email,
            "password": user.password  # Hash this in production
        }).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, current_user: str = Depends(verify_jwt_token)):
    response = supabase.table("users").select("*").eq("id", str(user_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    return response.data[0]

@router.get("/", response_model=List[UserResponse])
async def get_all_users(current_user: str = Depends(verify_jwt_token)):
    response = supabase.table("users").select("*").execute()
    return response.data

@router.delete("/{user_id}")
async def remove_user(user_id: UUID, current_user: str = Depends(verify_jwt_token)):
    response = supabase.table("users").delete().eq("id", str(user_id)).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}