"""Grid carbon intensity and carbon-aware scheduling endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.models import GridIntensitySnapshot, GridRegion, SchedulingEvent

router = APIRouter()

REGION_METADATA = {
    "us_east":      {"label": "US East (Virginia)",       "country": "US", "tz": "America/New_York"},
    "us_west":      {"label": "US West (Oregon)",         "country": "US", "tz": "America/Los_Angeles"},
    "eu_west":      {"label": "EU West (Ireland)",        "country": "IE", "tz": "Europe/Dublin"},
    "eu_north":     {"label": "EU North (Stockholm)",     "country": "SE", "tz": "Europe/Stockholm"},
    "asia_pacific": {"label": "Asia Pacific (Singapore)", "country": "SG", "tz": "Asia/Singapore"},
    "uk":           {"label": "United Kingdom",           "country": "GB", "tz": "Europe/London"},
    "canada":       {"label": "Canada (Montreal)",        "country": "CA", "tz": "America/Montreal"},
}


@router.get("/intensity/current")
def current_grid_intensity(db: Session = Depends(get_db)):
    """Latest grid carbon intensity for all regions."""
    result = []
    for region in GridRegion:
        snap = (
            db.query(GridIntensitySnapshot)
            .filter(GridIntensitySnapshot.region == region)
            .order_by(desc(GridIntensitySnapshot.timestamp))
            .first()
        )
        meta = REGION_METADATA.get(region.value, {})
        result.append({
            "region": region.value,
            "label": meta.get("label", region.value),
            "intensity_gco2e_kwh": snap.intensity if snap else None,
            "renewable_pct": snap.renewable_pct if snap else None,
            "timestamp": snap.timestamp.isoformat() if snap else None,
            "rating": _intensity_rating(snap.intensity if snap else 999),
        })
    result.sort(key=lambda x: x["intensity_gco2e_kwh"] or 9999)
    return result


@router.get("/intensity/history")
def grid_intensity_history(
    region: str = Query("us_east"),
    hours: int = Query(24, le=168),
    db: Session = Depends(get_db),
):
    """Historical grid intensity for a region."""
    from datetime import datetime, timedelta, timezone
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    try:
        region_enum = GridRegion(region)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown region: {region}")

    snaps = (
        db.query(GridIntensitySnapshot)
        .filter(
            GridIntensitySnapshot.region == region_enum,
            GridIntensitySnapshot.timestamp >= since,
        )
        .order_by(GridIntensitySnapshot.timestamp)
        .all()
    )
    return [
        {
            "timestamp": s.timestamp.isoformat(),
            "intensity": s.intensity,
            "renewable_pct": s.renewable_pct,
        }
        for s in snaps
    ]


@router.get("/schedule/recommend")
def recommend_schedule(
    workload_type: str = Query("batch"),
    duration_hours: float = Query(2.0),
    db: Session = Depends(get_db),
):
    """
    Recommend the best region and time window for a workload based on
    current and forecast grid carbon intensity.
    """
    current = []
    for region in GridRegion:
        snap = (
            db.query(GridIntensitySnapshot)
            .filter(GridIntensitySnapshot.region == region)
            .order_by(desc(GridIntensitySnapshot.timestamp))
            .first()
        )
        if snap:
            current.append({
                "region": region.value,
                "label": REGION_METADATA.get(region.value, {}).get("label", region.value),
                "intensity": snap.intensity,
                "renewable_pct": snap.renewable_pct,
            })

    current.sort(key=lambda x: x["intensity"])
    best = current[0] if current else None

    return {
        "workload_type": workload_type,
        "is_deferrable": workload_type in ("batch", "background", "training"),
        "recommended_region": best["region"] if best else None,
        "recommended_region_label": best["label"] if best else None,
        "recommended_intensity": best["intensity"] if best else None,
        "all_regions_ranked": current,
        "advice": (
            f"Schedule in {best['label']} ({best['intensity']:.0f} gCO2e/kWh) "
            f"for lowest carbon impact." if best else "No data available."
        ),
    }


@router.get("/scheduling-events")
def get_scheduling_events(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    events = (
        db.query(SchedulingEvent)
        .order_by(desc(SchedulingEvent.timestamp))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": e.id,
            "workload_id": e.workload_id,
            "event_type": e.event_type,
            "original_region": e.original_region.value if e.original_region else None,
            "selected_region": e.selected_region.value if e.selected_region else None,
            "original_intensity": e.original_intensity,
            "selected_intensity": e.selected_intensity,
            "carbon_saved_g": e.carbon_saved_g,
            "reason": e.reason,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]


def _intensity_rating(intensity: float) -> str:
    if intensity < 100:
        return "excellent"
    elif intensity < 200:
        return "good"
    elif intensity < 350:
        return "moderate"
    elif intensity < 500:
        return "poor"
    else:
        return "critical"
