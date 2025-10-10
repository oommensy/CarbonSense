from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router

# Create FastAPI app
app = FastAPI(
    title="CarbonSense API",
    description="Climate Action Tracker - Empowering individuals and corporations to make measurable environmental impact",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to CarbonSense API",
        "version": "1.0.0",
        "description": "Climate Action Tracker for individuals and corporations",
        "docs_url": "/docs",
        "features": [
            "Carbon footprint tracking",
            "Community challenges",
            "Impact verification",
            "Corporate ESG dashboard",
            "AI-powered recommendations"
        ],
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "CarbonSense API",
            "version": "1.0.0"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
    )