"""
CarbonSense API v2 — AI Energy Observability Platform
The Datadog for AI sustainability: GPU/NPU telemetry, carbon-aware inference,
green scores, Pareto dashboards, and model optimization recommendations.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.v1.api import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("carbonsense")

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CarbonSense API v2 starting up...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified.")

    # Seed demo data
    db = SessionLocal()
    try:
        from app.utils.seed_data import seed_all
        seed_all(db)
    except Exception as e:
        logger.warning(f"Seed data warning: {e}")
    finally:
        db.close()

    logger.info("CarbonSense API ready.")
    yield
    logger.info("CarbonSense API shutting down.")


app = FastAPI(
    title="CarbonSense API",
    description=(
        "**The Datadog for AI Energy & Sustainability.**\n\n"
        "Monitor GPU/NPU telemetry, track carbon per inference, "
        "optimize models for energy efficiency, and schedule workloads "
        "carbon-aware across regions."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info("%s %s → %s", request.method, request.url.path, response.status_code)
    return response


app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
async def root():
    return {
        "service": "CarbonSense API",
        "version": "2.0.0",
        "tagline": "The Datadog for AI Energy & Sustainability",
        "docs": "/docs",
        "capabilities": [
            "GPU/NPU real-time telemetry ingestion",
            "Carbon per inference tracking (DEFRA 2024 / EPA 2023)",
            "Energy vs Latency Pareto frontier analysis",
            "Green Score for inference pipelines (0–100)",
            "Model optimization recommendations (quantization, batching, right-sizing)",
            "Carbon-aware inference scheduling",
            "Edge vs Cloud cost/energy/carbon comparison",
            "Grid carbon intensity (7 regions, real-time)",
        ],
    }


@app.get("/health", tags=["root"])
async def health():
    return JSONResponse({"status": "healthy", "version": "2.0.0"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
