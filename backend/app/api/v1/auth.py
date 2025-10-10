from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.models import get_db, User, UserRole
from app.auth import AuthService, get_current_active_user
from app.schemas.auth import UserCreate, UserResponse, Token

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    role: UserRole = UserRole.INDIVIDUAL

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """User registration"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        is_verified=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        username=db_user.username,
        full_name=db_user.full_name,
        role=db_user.role,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        carbon_goal=db_user.carbon_goal,
        created_at=db_user.created_at
    )

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """User login"""
    
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not AuthService.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    refresh_token = AuthService.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    
    try:
        payload = AuthService.verify_token(refresh_token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=30)
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        new_refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=1800
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """User logout"""
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just return a success message
    return {
        "message": "Successfully logged out",
        "user_id": current_user.id
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        carbon_goal=current_user.carbon_goal,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at
    )