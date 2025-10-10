from fastapi import APIRouter
from app.api.v1 import auth, users, carbon, challenges, corporate, analytics

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(carbon.router, prefix="/carbon", tags=["carbon-tracking"])
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(corporate.router, prefix="/corporate", tags=["corporate"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])