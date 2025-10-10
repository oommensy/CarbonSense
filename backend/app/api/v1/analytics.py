from fastapi import APIRouter

router = APIRouter()

@router.get("/insights")
async def get_analytics_insights():
    """Get analytics insights"""
    return {"message": "Analytics insights endpoint"}

@router.get("/reports")
async def get_analytics_reports():
    """Get analytics reports"""
    return {"message": "Analytics reports endpoint"}