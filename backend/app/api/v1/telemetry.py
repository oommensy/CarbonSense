"""Telemetry ingestion and retrieval endpoints."""
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.models import GPUTelemetry, HardwareNode, AIWorkload

router = APIRouter()


@router.get("/live")
def get_live_telemetry(
    node_id: Optional[int] = None,
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
):
    """Latest telemetry samples across all nodes."""
    q = db.query(GPUTelemetry).order_by(desc(GPUTelemetry.timestamp))
    if node_id:
        q = q.filter(GPUTelemetry.node_id == node_id)
    samples = q.limit(limit).all()
    return [_telem_dict(s) for s in samples]


@router.get("/nodes")
def get_nodes(db: Session = Depends(get_db)):
    """All registered hardware nodes."""
    nodes = db.query(HardwareNode).filter(HardwareNode.is_active == True).all()
    return [_node_dict(n) for n in nodes]


@router.get("/nodes/{node_id}/history")
def get_node_history(
    node_id: int,
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db),
):
    """Time-series telemetry for a specific node."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    samples = (
        db.query(GPUTelemetry)
        .filter(GPUTelemetry.node_id == node_id, GPUTelemetry.timestamp >= since)
        .order_by(GPUTelemetry.timestamp)
        .all()
    )
    return [_telem_dict(s) for s in samples]


@router.get("/summary")
def get_telemetry_summary(db: Session = Depends(get_db)):
    """Aggregate utilization and power summary across all nodes."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    row = db.query(
        func.avg(GPUTelemetry.gpu_utilization_pct).label("avg_util"),
        func.avg(GPUTelemetry.power_draw_watts).label("avg_power"),
        func.sum(GPUTelemetry.energy_kwh).label("total_energy"),
        func.sum(GPUTelemetry.carbon_g_co2e).label("total_carbon_g"),
        func.avg(GPUTelemetry.tokens_per_second).label("avg_tps"),
    ).filter(GPUTelemetry.timestamp >= since).first()

    return {
        "period_hours": 24,
        "avg_gpu_utilization_pct": round(row.avg_util or 0, 1),
        "avg_power_watts": round(row.avg_power or 0, 1),
        "total_energy_kwh": round(row.total_energy or 0, 3),
        "total_carbon_g_co2e": round(row.total_carbon_g or 0, 2),
        "avg_tokens_per_second": round(row.avg_tps or 0, 1),
    }


def _telem_dict(s: GPUTelemetry):
    return {
        "id": s.id,
        "node_id": s.node_id,
        "workload_id": s.workload_id,
        "timestamp": s.timestamp.isoformat() if s.timestamp else None,
        "gpu_utilization_pct": s.gpu_utilization_pct,
        "memory_used_gb": s.memory_used_gb,
        "memory_utilization_pct": s.memory_utilization_pct,
        "power_draw_watts": s.power_draw_watts,
        "temperature_c": s.temperature_c,
        "energy_kwh": s.energy_kwh,
        "carbon_g_co2e": s.carbon_g_co2e,
        "grid_intensity": s.grid_intensity,
        "tokens_per_second": s.tokens_per_second,
        "batch_size": s.batch_size,
    }


def _node_dict(n: HardwareNode):
    return {
        "id": n.id,
        "name": n.name,
        "hardware_type": n.hardware_type.value if n.hardware_type else None,
        "deployment": n.deployment.value if n.deployment else None,
        "grid_region": n.grid_region.value if n.grid_region else None,
        "count": n.count,
        "tdp_watts": n.tdp_watts,
        "memory_gb": n.memory_gb,
        "cloud_instance": n.cloud_instance,
        "cost_per_hour": n.cost_per_hour,
    }
