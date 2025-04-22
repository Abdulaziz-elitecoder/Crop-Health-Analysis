from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str = None 

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False  # Add is_admin flag, default to False

class UserSignIn(BaseModel):
    email: EmailStr
    password: str
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_admin: bool = False  # Add is_admin flag, default to False


class UserResponse(BaseModel):
    id: UUID
    auth_user_id: UUID 
    email: EmailStr
    created_at: datetime
    is_admin: bool = False  # Add is_admin flag, default to False

    class Config:
        from_attributes = True
class ImageCreate(BaseModel):
    metadata: Optional[Dict[str, Any]] = None

class ImageResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str

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

class PredictionResponse(BaseModel):
    class_name: str
    confidence: float

class LogCreate(BaseModel):
    user_id: UUID 
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