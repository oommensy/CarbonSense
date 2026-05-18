"""Inference pipeline management and green score endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.models import InferencePipeline, AIWorkload, OptimizationRecommendation
from app.services.recommendations import generate_recommendations, edge_vs_cloud_analysis

router = APIRouter()


@router.get("/")
def list_pipelines(db: Session = Depends(get_db)):
    pipelines = db.query(InferencePipeline).filter(InferencePipeline.is_active == True).all()
    result = []
    for p in pipelines:
        stats = _pipeline_stats(p.id, db)
        result.append({**_pipeline_dict(p), **stats})
    return result


@router.get("/{pipeline_id}")
def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    p = db.query(InferencePipeline).filter(InferencePipeline.id == pipeline_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    stats = _pipeline_stats(pipeline_id, db)
    recs = db.query(OptimizationRecommendation).filter(
        OptimizationRecommendation.pipeline_id == pipeline_id
    ).order_by(OptimizationRecommendation.created_at.desc()).all()
    return {
        **_pipeline_dict(p),
        **stats,
        "recommendations": [_rec_dict(r) for r in recs],
    }


@router.get("/{pipeline_id}/recommendations")
def get_recommendations(pipeline_id: int, db: Session = Depends(get_db)):
    recs = (
        db.query(OptimizationRecommendation)
        .filter(OptimizationRecommendation.pipeline_id == pipeline_id)
        .order_by(OptimizationRecommendation.created_at.desc())
        .all()
    )
    return [_rec_dict(r) for r in recs]


@router.post("/{pipeline_id}/analyze")
def analyze_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    """Run the recommendations engine on the latest workload stats for a pipeline."""
    p = db.query(InferencePipeline).filter(InferencePipeline.id == pipeline_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    stats = _pipeline_stats(pipeline_id, db)
    latest_wl = (
        db.query(AIWorkload)
        .filter(AIWorkload.pipeline_id == pipeline_id)
        .order_by(desc(AIWorkload.started_at))
        .first()
    )

    workload_stats = {
        "quantization": latest_wl.quantization if latest_wl else "fp16",
        "avg_batch_size": stats.get("avg_batch_size", 4),
        "avg_gpu_utilization_pct": stats.get("avg_gpu_util", 50),
        "model_params_b": latest_wl.model_params_b if latest_wl else 7,
        "deployment": p.deployment.value if p.deployment else "cloud_aws",
        "grid_intensity_gco2e": stats.get("avg_grid_intensity", 386),
        "avg_latency_ms": stats.get("avg_latency_ms", 300),
        "carbon_aware_pct": 10,
        "hardware_type": latest_wl.node.hardware_type.value if latest_wl and latest_wl.node else "gpu_nvidia_a100",
        "cost_per_hour": latest_wl.node.cost_per_hour if latest_wl and latest_wl.node else 3.0,
    }

    recs_data = generate_recommendations(workload_stats)

    # Persist new recommendations
    for rd in recs_data:
        existing = db.query(OptimizationRecommendation).filter(
            OptimizationRecommendation.pipeline_id == pipeline_id,
            OptimizationRecommendation.rec_type == rd["rec_type"],
            OptimizationRecommendation.is_applied == False,
        ).first()
        if not existing:
            rec = OptimizationRecommendation(
                pipeline_id=pipeline_id,
                rec_type=rd["rec_type"],
                priority=rd["priority"],
                title=rd["title"],
                description=rd["description"],
                rationale=rd["rationale"],
                estimated_energy_saving_pct=rd["estimated_energy_saving_pct"],
                estimated_carbon_saving_pct=rd["estimated_carbon_saving_pct"],
                estimated_cost_saving_usd=rd["estimated_cost_saving_usd"],
                estimated_latency_change_pct=rd["estimated_latency_change_pct"],
                confidence_score=rd["confidence_score"],
                action_steps=rd["action_steps"],
            )
            db.add(rec)

    db.commit()
    return {"message": f"Generated {len(recs_data)} recommendations", "recommendations": recs_data}


@router.get("/{pipeline_id}/edge-vs-cloud")
def edge_vs_cloud(
    pipeline_id: int,
    monthly_requests: int = 100000,
    avg_tokens: int = 500,
    db: Session = Depends(get_db),
):
    p = db.query(InferencePipeline).filter(InferencePipeline.id == pipeline_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    latest_wl = (
        db.query(AIWorkload)
        .filter(AIWorkload.pipeline_id == pipeline_id)
        .order_by(desc(AIWorkload.started_at))
        .first()
    )

    return edge_vs_cloud_analysis(
        model_params_b=latest_wl.model_params_b if latest_wl else 7,
        monthly_requests=monthly_requests,
        avg_tokens_per_request=avg_tokens,
        cloud_cost_per_hour=latest_wl.node.cost_per_hour if latest_wl and latest_wl.node else 3.0,
        cloud_grid_intensity=386.0,
        edge_tdp_watts=15.0,
        edge_grid_intensity=150.0,
        edge_hardware_cost_usd=500.0,
    )


def _pipeline_stats(pipeline_id: int, db: Session):
    from datetime import timedelta, timezone
    from datetime import datetime
    since = datetime.now(timezone.utc) - timedelta(days=7)
    row = db.query(
        func.count(AIWorkload.id).label("runs"),
        func.avg(AIWorkload.green_score).label("green_score"),
        func.sum(AIWorkload.total_energy_kwh).label("energy"),
        func.sum(AIWorkload.total_carbon_g_co2e).label("carbon_g"),
        func.avg(AIWorkload.avg_latency_ms).label("latency"),
        func.sum(AIWorkload.compute_cost_usd).label("cost"),
        func.sum(AIWorkload.total_requests).label("requests"),
    ).filter(
        AIWorkload.pipeline_id == pipeline_id,
        AIWorkload.started_at >= since,
    ).first()

    return {
        "runs_7d": row.runs or 0,
        "avg_green_score": round(row.green_score or 0, 1),
        "total_energy_kwh_7d": round(row.energy or 0, 3),
        "total_carbon_kg_7d": round((row.carbon_g or 0) / 1000, 4),
        "avg_latency_ms": round(row.latency or 0, 1),
        "total_cost_usd_7d": round(row.cost or 0, 2),
        "total_requests_7d": row.requests or 0,
    }


def _pipeline_dict(p: InferencePipeline):
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "model_name": p.model_name,
        "framework": p.framework.value if p.framework else None,
        "deployment": p.deployment.value if p.deployment else None,
        "is_active": p.is_active,
        "current_green_score": p.current_green_score,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def _rec_dict(r: OptimizationRecommendation):
    return {
        "id": r.id,
        "rec_type": r.rec_type.value if r.rec_type else None,
        "priority": r.priority.value if r.priority else None,
        "title": r.title,
        "description": r.description,
        "rationale": r.rationale,
        "estimated_energy_saving_pct": r.estimated_energy_saving_pct,
        "estimated_carbon_saving_pct": r.estimated_carbon_saving_pct,
        "estimated_cost_saving_usd": r.estimated_cost_saving_usd,
        "estimated_latency_change_pct": r.estimated_latency_change_pct,
        "confidence_score": r.confidence_score,
        "action_steps": r.action_steps,
        "is_applied": r.is_applied,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
