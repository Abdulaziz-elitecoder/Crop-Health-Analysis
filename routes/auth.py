# routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from config import supabase, JWT_SECRET
from models import UserSignUp, UserSignIn, Token, UserResponse
from datetime import datetime, timedelta
import jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/signin")

# JWT token creation
def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# JWT token validation
def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/signup", response_model=Token)
async def signup(user: UserSignUp):
    try:
        # Sign up user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        if not response.user:
            raise HTTPException(status_code=400, detail="Sign-up failed")

        user_id = str(response.user.id)
        email = response.user.email

        # Insert into custom users table (include password)
        supabase.table("users").insert({
            "auth_user_id": user_id,
            "email": email,
            "password": user.password,  # Add password here
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # Create a custom JWT token for the user
        token = create_jwt_token(user_id, email)

        return Token(access_token=token, token_type="bearer")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signin", response_model=Token)
async def signin(user: UserSignIn):
    try:
        # Sign in user with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = str(response.user.id)
        email = response.user.email

        # Create a custom JWT token for the user
        token = create_jwt_token(user_id, email)

        return Token(access_token=token, token_type="bearer")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        # Sign out from Supabase Auth
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(verify_jwt_token)):
    response = supabase.table("users").select("*").eq("auth_user_id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    return response.data[0]