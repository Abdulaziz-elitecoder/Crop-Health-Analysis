# routers/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import EmailStr
from typing import Dict
from services.auth import signup, signin, logout

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup")
async def signup_route(email: EmailStr, password: str) -> Dict:
    try:
        user_data = await signup(email, password)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin")
async def signin_route(email: EmailStr, password: str) -> Dict:
    try:
        user_data = await signin(email, password)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout_route(access_token: str):
    try:
        await logout(access_token)
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))