"""
Safety Monitor API — CarbonSense v2
=====================================
Endpoints for safety evaluation, safety event history, and pipeline safety summaries.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.models.models import (
    AIWorkload, InferencePipeline, SafetyEvent,
    SafetyEventType, SafetySeverity,
)
from app.services.safety import evaluate_workload

router = APIRouter(prefix="/safety", tags=["safety"])


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response schemas
# ─────────────────────────────────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    prompt: Optional[str] = None
    response: Optional[str] = None
    model_name: Optional[str] = None
    quantization: Optional[str] = None


class EvaluateResponse(BaseModel):
    safety_score: float
    hallucination_risk: float
    toxicity_score: float
    pii_detected: bool
    pii_count: int
    injection_attempts: int
    safety_violations: int
    safety_events: list
    eval_ms: float


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest):
    """
    Evaluate a prompt/response pair for safety violations.
    Returns a composite safety score and per-check findings.
    """
    result = evaluate_workload(
        prompt=req.prompt,
        response=req.response,
        model_name=req.model_name,
        quantization=req.quantization,
    )
    return result.to_dict()


@router.get("/summary")
def safety_summary(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    """
    Aggregate safety metrics across all workloads for the last N days.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    workloads = (
        db.query(AIWorkload)
        .filter(AIWorkload.started_at >= since)
        .filter(AIWorkload.safety_score.isnot(None))
        .all()
    )

    if not workloads:
        return {
            "total_workloads": 0,
            "avg_safety_score": 100.0,
            "avg_hallucination_risk": 0.0,
            "avg_toxicity_score": 0.0,
            "total_pii_incidents": 0,
            "total_injection_attempts": 0,
            "total_safety_violations": 0,
            "safety_score_trend": [],
        }

    avg_safety    = sum(w.safety_score or 100 for w in workloads) / len(workloads)
    avg_halluc    = sum(w.hallucination_risk or 0 for w in workloads) / len(workloads)
    avg_toxicity  = sum(w.toxicity_score or 0 for w in workloads) / len(workloads)
    total_pii     = sum(w.pii_count or 0 for w in workloads)
    total_inject  = sum(w.injection_attempts or 0 for w in workloads)
    total_violate = sum(w.safety_violations or 0 for w in workloads)

    # Daily trend
    from collections import defaultdict
    daily: dict = defaultdict(list)
    for w in workloads:
        if w.started_at:
            day = w.started_at.strftime("%Y-%m-%d")
            daily[day].append(w.safety_score or 100)
    trend = [
        {"date": d, "avg_safety_score": round(sum(v) / len(v), 1)}
        for d, v in sorted(daily.items())
    ]

    return {
        "total_workloads": len(workloads),
        "avg_safety_score": round(avg_safety, 1),
        "avg_hallucination_risk": round(avg_halluc, 3),
        "avg_toxicity_score": round(avg_toxicity, 3),
        "total_pii_incidents": total_pii,
        "total_injection_attempts": total_inject,
        "total_safety_violations": total_violate,
        "safety_score_trend": trend,
    }


@router.get("/events")
def list_safety_events(
    days: int = Query(7, ge=1, le=90),
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """List recent safety events, optionally filtered by severity or type."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = db.query(SafetyEvent).filter(SafetyEvent.timestamp >= since)
    if severity:
        try:
            q = q.filter(SafetyEvent.severity == SafetySeverity(severity))
        except ValueError:
            raise HTTPException(400, f"Invalid severity: {severity}")
    if event_type:
        try:
            q = q.filter(SafetyEvent.event_type == SafetyEventType(event_type))
        except ValueError:
            raise HTTPException(400, f"Invalid event_type: {event_type}")
    events = q.order_by(desc(SafetyEvent.timestamp)).limit(limit).all()
    return [
        {
            "id": e.id,
            "workload_id": e.workload_id,
            "event_type": e.event_type.value if e.event_type else None,
            "severity": e.severity.value if e.severity else None,
            "detail": e.detail,
            "score": e.score,
            "blocked": e.blocked,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]


@router.get("/events/counts")
def event_type_counts(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    """Count safety events by type for the last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(SafetyEvent.event_type, func.count(SafetyEvent.id))
        .filter(SafetyEvent.timestamp >= since)
        .group_by(SafetyEvent.event_type)
        .all()
    )
    return [{"event_type": r[0].value if r[0] else "unknown", "count": r[1]} for r in rows]


@router.get("/pipeline/{pipeline_id}")
def pipeline_safety(pipeline_id: int, days: int = Query(30, ge=1, le=90), db: Session = Depends(get_db)):
    """Safety metrics for a specific pipeline."""
    pipeline = db.query(InferencePipeline).filter(InferencePipeline.id == pipeline_id).first()
    if not pipeline:
        raise HTTPException(404, "Pipeline not found")

    since = datetime.now(timezone.utc) - timedelta(days=days)
    workloads = (
        db.query(AIWorkload)
        .filter(AIWorkload.pipeline_id == pipeline_id)
        .filter(AIWorkload.started_at >= since)
        .filter(AIWorkload.safety_score.isnot(None))
        .all()
    )

    if not workloads:
        return {"pipeline_id": pipeline_id, "pipeline_name": pipeline.name, "workloads": 0}

    return {
        "pipeline_id": pipeline_id,
        "pipeline_name": pipeline.name,
        "workloads": len(workloads),
        "avg_safety_score": round(sum(w.safety_score or 100 for w in workloads) / len(workloads), 1),
        "avg_hallucination_risk": round(sum(w.hallucination_risk or 0 for w in workloads) / len(workloads), 3),
        "total_pii_incidents": sum(w.pii_count or 0 for w in workloads),
        "total_injection_attempts": sum(w.injection_attempts or 0 for w in workloads),
        "total_safety_violations": sum(w.safety_violations or 0 for w in workloads),
        "quantization": workloads[-1].quantization if workloads else None,
    }


@router.get("/workload/{workload_id}")
def workload_safety(workload_id: int, db: Session = Depends(get_db)):
    """Full safety details for a specific workload."""
    w = db.query(AIWorkload).filter(AIWorkload.id == workload_id).first()
    if not w:
        raise HTTPException(404, "Workload not found")
    return {
        "workload_id": w.id,
        "model_name": w.model_name,
        "quantization": w.quantization,
        "safety_score": w.safety_score,
        "hallucination_risk": w.hallucination_risk,
        "toxicity_score": w.toxicity_score,
        "pii_detected": w.pii_detected,
        "pii_count": w.pii_count,
        "injection_attempts": w.injection_attempts,
        "safety_violations": w.safety_violations,
        "safety_events": w.safety_events or [],
    }
