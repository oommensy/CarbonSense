from fastapi import APIRouter

router = APIRouter()

@router.get("/profile")
async def get_profile():
    """Get user profile"""
    return {"message": "User profile endpoint"}

@router.put("/profile")
async def update_profile():
    """Update user profile""" 
    return {"message": "Update profile endpoint"}