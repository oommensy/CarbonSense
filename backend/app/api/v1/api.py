from fastapi import APIRouter
from app.api.v1 import telemetry, workloads, pipelines, carbon

api_router = APIRouter()

api_router.include_router(telemetry.router, prefix="/telemetry", tags=["Telemetry"])
api_router.include_router(workloads.router, prefix="/workloads", tags=["Workloads"])
api_router.include_router(pipelines.router, prefix="/pipelines", tags=["Pipelines"])
api_router.include_router(carbon.router, prefix="/carbon", tags=["Carbon"])
