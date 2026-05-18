"""AI Workload management and analytics endpoints."""
from typing import Optional, List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.models import AIWorkload, HardwareNode, InferencePipeline

router = APIRouter()


@router.get("/")
def list_workloads(
    pipeline_id: Optional[int] = None,
    days: int = Query(7, le=90),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(AIWorkload).filter(AIWorkload.started_at >= since)
    if pipeline_id:
        q = q.filter(AIWorkload.pipeline_id == pipeline_id)
    workloads = q.order_by(desc(AIWorkload.started_at)).limit(limit).all()
    return [_wl_dict(w) for w in workloads]


@router.get("/summary")
def workload_summary(
    days: int = Query(7, le=90),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    row = db.query(
        func.count(AIWorkload.id).label("total_runs"),
        func.sum(AIWorkload.total_energy_kwh).label("total_energy"),
        func.sum(AIWorkload.total_carbon_g_co2e).label("total_carbon_g"),
        func.sum(AIWorkload.compute_cost_usd).label("total_cost"),
        func.avg(AIWorkload.green_score).label("avg_green_score"),
        func.avg(AIWorkload.avg_latency_ms).label("avg_latency"),
        func.sum(AIWorkload.total_tokens).label("total_tokens"),
        func.sum(AIWorkload.total_requests).label("total_requests"),
    ).filter(AIWorkload.started_at >= since).first()

    return {
        "period_days": days,
        "total_runs": row.total_runs or 0,
        "total_energy_kwh": round(row.total_energy or 0, 3),
        "total_carbon_kg": round((row.total_carbon_g or 0) / 1000, 3),
        "total_cost_usd": round(row.total_cost or 0, 2),
        "avg_green_score": round(row.avg_green_score or 0, 1),
        "avg_latency_ms": round(row.avg_latency or 0, 1),
        "total_tokens": row.total_tokens or 0,
        "total_requests": row.total_requests or 0,
    }


@router.get("/pareto")
def energy_latency_pareto(
    days: int = Query(7, le=90),
    db: Session = Depends(get_db),
):
    """
    Returns data for the Energy vs Latency Pareto frontier chart.
    Each point = one workload run, with energy/request and latency.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    workloads = (
        db.query(AIWorkload)
        .filter(
            AIWorkload.started_at >= since,
            AIWorkload.total_energy_kwh.isnot(None),
            AIWorkload.avg_latency_ms.isnot(None),
            AIWorkload.total_requests > 0,
        )
        .all()
    )

    points = []
    for w in workloads:
        energy_per_req = (w.total_energy_kwh * 1000) / max(w.total_requests, 1)  # Wh/req
        points.append({
            "id": w.id,
            "name": w.name,
            "model": w.model_name,
            "quantization": w.quantization,
            "hardware": w.node.hardware_type.value if w.node else "unknown",
            "energy_wh_per_request": round(energy_per_req, 4),
            "latency_ms": round(w.avg_latency_ms, 1),
            "carbon_g_per_request": round((w.total_carbon_g_co2e or 0) / max(w.total_requests, 1), 4),
            "green_score": w.green_score,
            "cost_per_1k_tokens": w.cost_per_1k_tokens,
            "throughput_tps": w.throughput_tps,
        })

    # Compute Pareto frontier (minimize both energy and latency)
    pareto = _pareto_frontier(points)
    return {"points": points, "pareto_frontier": pareto}


@router.get("/by-model")
def workloads_by_model(
    days: int = Query(7, le=90),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            AIWorkload.model_name,
            func.count(AIWorkload.id).label("runs"),
            func.sum(AIWorkload.total_energy_kwh).label("energy"),
            func.sum(AIWorkload.total_carbon_g_co2e).label("carbon_g"),
            func.avg(AIWorkload.green_score).label("green_score"),
            func.avg(AIWorkload.avg_latency_ms).label("latency"),
            func.sum(AIWorkload.compute_cost_usd).label("cost"),
        )
        .filter(AIWorkload.started_at >= since)
        .group_by(AIWorkload.model_name)
        .all()
    )
    return [
        {
            "model": r.model_name,
            "runs": r.runs,
            "total_energy_kwh": round(r.energy or 0, 3),
            "total_carbon_kg": round((r.carbon_g or 0) / 1000, 4),
            "avg_green_score": round(r.green_score or 0, 1),
            "avg_latency_ms": round(r.latency or 0, 1),
            "total_cost_usd": round(r.cost or 0, 2),
        }
        for r in rows
    ]


@router.get("/{workload_id}")
def get_workload(workload_id: int, db: Session = Depends(get_db)):
    w = db.query(AIWorkload).filter(AIWorkload.id == workload_id).first()
    if not w:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Workload not found")
    return _wl_dict(w)


def _pareto_frontier(points):
    """Return points that are not dominated (lower energy AND lower latency)."""
    frontier = []
    for p in points:
        dominated = False
        for q in points:
            if q["id"] == p["id"]:
                continue
            if (q["energy_wh_per_request"] <= p["energy_wh_per_request"] and
                    q["latency_ms"] <= p["latency_ms"] and
                    (q["energy_wh_per_request"] < p["energy_wh_per_request"] or
                     q["latency_ms"] < p["latency_ms"])):
                dominated = True
                break
        if not dominated:
            frontier.append(p)
    return sorted(frontier, key=lambda x: x["energy_wh_per_request"])


def _wl_dict(w: AIWorkload):
    return {
        "id": w.id,
        "name": w.name,
        "model_name": w.model_name,
        "workload_type": w.workload_type.value if w.workload_type else None,
        "framework": w.framework.value if w.framework else None,
        "quantization": w.quantization,
        "model_params_b": w.model_params_b,
        "started_at": w.started_at.isoformat() if w.started_at else None,
        "ended_at": w.ended_at.isoformat() if w.ended_at else None,
        "duration_seconds": w.duration_seconds,
        "total_energy_kwh": w.total_energy_kwh,
        "total_carbon_g_co2e": w.total_carbon_g_co2e,
        "avg_power_watts": w.avg_power_watts,
        "total_tokens": w.total_tokens,
        "total_requests": w.total_requests,
        "avg_latency_ms": w.avg_latency_ms,
        "p99_latency_ms": w.p99_latency_ms,
        "throughput_tps": w.throughput_tps,
        "compute_cost_usd": w.compute_cost_usd,
        "cost_per_1k_tokens": w.cost_per_1k_tokens,
        "green_score": w.green_score,
        "green_score_breakdown": w.green_score_breakdown,
        "status": w.status,
        "tags": w.tags,
        "hardware_type": w.node.hardware_type.value if w.node else None,
        "pipeline_name": w.pipeline.name if w.pipeline else None,
    }
