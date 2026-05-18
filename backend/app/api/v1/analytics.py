"""
Correlation Analytics API — CarbonSense v2
==========================================
Trade-off intelligence endpoints: optimization impact, correlation matrix,
model comparisons, and the global insights feed.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.correlation import engine as correlation_engine

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/insights")
def global_insights(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    """
    Global trade-off insights feed — the 'homepage' of the correlation engine.
    Returns the most significant optimization trade-offs detected across all pipelines.
    """
    return correlation_engine.global_summary(db=db, days=days)


@router.get("/pipeline/{pipeline_id}/tradeoffs")
def pipeline_tradeoffs(
    pipeline_id: int,
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """
    Full optimization impact report for a specific pipeline.
    Includes quantization, deployment, and batching trade-off insights.
    """
    report = correlation_engine.analyze_pipeline(pipeline_id=pipeline_id, db=db, days=days)
    return report.to_dict()


@router.get("/model/{model_name}/tradeoffs")
def model_tradeoffs(
    model_name: str,
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """
    Trade-off analysis for a specific model across all pipelines.
    Useful for comparing quantization variants of the same model.
    """
    report = correlation_engine.analyze_model(model_name=model_name, db=db, days=days)
    return report.to_dict()


@router.get("/correlations")
def global_correlations(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    """
    Pairwise metric correlations across all workloads.
    Returns correlation coefficients between carbon, latency, safety, energy, cost.
    """
    summary = correlation_engine.global_summary(db=db, days=days)
    return summary.get("correlation_matrix", {"pairs": []})


@router.get("/scatter")
def scatter_data(
    x: str = Query("total_carbon_g_co2e", description="X-axis metric"),
    y: str = Query("safety_score", description="Y-axis metric"),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """
    Raw scatter plot data for any two metrics.
    Used by the Trade-off Intelligence dashboard page.
    """
    from datetime import datetime, timedelta, timezone
    from app.models.models import AIWorkload

    since = datetime.now(timezone.utc) - timedelta(days=days)
    workloads = (
        db.query(AIWorkload)
        .filter(AIWorkload.started_at >= since)
        .filter(AIWorkload.status == "completed")
        .all()
    )

    METRIC_MAP = {
        "total_carbon_g_co2e": lambda w: w.total_carbon_g_co2e,
        "safety_score": lambda w: w.safety_score,
        "hallucination_risk": lambda w: w.hallucination_risk,
        "avg_latency_ms": lambda w: w.avg_latency_ms,
        "total_energy_kwh": lambda w: w.total_energy_kwh,
        "compute_cost_usd": lambda w: w.compute_cost_usd,
        "toxicity_score": lambda w: w.toxicity_score,
        "throughput_tps": lambda w: w.throughput_tps,
        "green_score": lambda w: w.green_score,
    }

    if x not in METRIC_MAP or y not in METRIC_MAP:
        raise HTTPException(400, f"Unknown metric. Valid: {list(METRIC_MAP.keys())}")

    points = []
    for w in workloads:
        xv = METRIC_MAP[x](w)
        yv = METRIC_MAP[y](w)
        if xv is not None and yv is not None:
            points.append({
                "x": round(xv, 4),
                "y": round(yv, 4),
                "model": w.model_name,
                "quantization": w.quantization,
                "workload_id": w.id,
            })

    return {"x_metric": x, "y_metric": y, "points": points, "count": len(points)}
