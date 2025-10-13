from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .carbon import router as carbon_router
from .challenges import router as challenges_router
from .analytics import router as analytics_router
from .corporate import router as corporate_router
from .social import router as social_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(carbon_router, prefix="/carbon", tags=["carbon tracking"])
api_router.include_router(challenges_router, prefix="/challenges", tags=["challenges"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(corporate_router, prefix="/corporate", tags=["corporate"])
api_router.include_router(social_router, prefix="/social", tags=["social media"])