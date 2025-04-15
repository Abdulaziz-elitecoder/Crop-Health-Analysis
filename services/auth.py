# services/auth.py
from database.supabase import get_supabase
from pydantic import EmailStr
from uuid import UUID

async def signup(email: EmailStr, password: str) -> dict:
    supabase = await get_supabase()
    try:
        # Sign up with Supabase Auth
        auth_response = await supabase.auth.sign_up({"email": email, "password": password})
        if not auth_response.user:
            raise ValueError("Signup failed: User not created")
        
        user_id = auth_response.user.id
        # Insert into users table
        user_data = {
            "id": str(UUID(user_id)),
            "auth_user_id": user_id,
            "email": email
        }
        response = await supabase.table("users").insert(user_data).execute()
        if not response.data:
            raise ValueError("Failed to store user in database")
        
        return {
            "user_id": user_id,
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token
        }
    except Exception as e:
        raise ValueError(f"Signup failed: {str(e)}")

async def signin(email: EmailStr, password: str) -> dict:
    supabase = await get_supabase()
    try:
        auth_response = await supabase.auth.sign_in_with_password({"email": email, "password": password})
        if not auth_response.user:
            raise ValueError("Signin failed: Invalid credentials")
        
        return {
            "user_id": auth_response.user.id,
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token
        }
    except Exception as e:
        raise ValueError(f"Signin failed: {str(e)}")

async def logout(access_token: str):
    supabase = await get_supabase()
    try:
        await supabase.auth.sign_out()
    except Exception as e:
        raise ValueError(f"Logout failed: {str(e)}")