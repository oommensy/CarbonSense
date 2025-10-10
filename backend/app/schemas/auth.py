from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.INDIVIDUAL

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    carbon_goal: Optional[float] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    carbon_goal: float
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None