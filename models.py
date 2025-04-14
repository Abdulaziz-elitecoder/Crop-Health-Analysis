# models.py
from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserSignUp(BaseModel):
    email: EmailStr
    password: str

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

# Existing Models (updated to reference auth.users)
# # User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    auth_user_id: UUID  # Add this to match the table
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class ImageCreate(BaseModel):
    user_id: UUID  # This will now reference auth.users(id)
    image_url: str
    metadata: Optional[Dict[str, Any]] = None

class ImageResponse(BaseModel):
    id: UUID
    user_id: UUID
    image_url: str
    metadata: Optional[Dict[str, Any]]
    uploaded_at: datetime

    class Config:
        from_attributes = True

class ClassificationCreate(BaseModel):
    image_id: UUID
    ndvi_value: float
    classification: str

class ClassificationResponse(BaseModel):
    id: UUID
    image_id: UUID
    ndvi_value: float
    classification: str
    created_at: datetime

    class Config:
        from_attributes = True

class LogCreate(BaseModel):
    user_id: UUID  # This will now reference auth.users(id)
    action: str
    details: Optional[Dict[str, Any]] = None

class LogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    details: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True