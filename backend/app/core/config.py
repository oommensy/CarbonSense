import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "CarbonSense"
    VERSION: str = "2.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./carbonsense.db")

    SECRET_KEY: str = "carbonsense-ai-observability-secret-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://0.0.0.0:3000",
    ]

    # Grid carbon intensity defaults (gCO2e/kWh) by region
    GRID_INTENSITY_US_EAST: float = 386.0
    GRID_INTENSITY_US_WEST: float = 210.0
    GRID_INTENSITY_EU_WEST: float = 233.0
    GRID_INTENSITY_ASIA_PACIFIC: float = 520.0
    GRID_INTENSITY_UK: float = 207.0

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
