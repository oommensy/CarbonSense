import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "CarbonSense"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/carbonsense"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:19006",
        "https://carbonsense.com",
        "https://app.carbonsense.com"
    ]
    
    # External APIs
    GOOGLE_MAPS_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    NASA_API_KEY: str = ""
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Cloud Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = "carbonsense-assets"
    AWS_REGION: str = "us-east-1"
    
    # Payment
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()