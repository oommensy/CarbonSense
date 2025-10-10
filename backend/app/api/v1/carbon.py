from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.models import get_db, CarbonEntry, CarbonCategory, User
from app.auth import get_current_active_user
from app.schemas.carbon import (
    CarbonEntryCreate,
    CarbonEntryResponse,
    CarbonSummary,
    CarbonGoals,
    CarbonTrend
)

router = APIRouter()

@router.post("/entries", response_model=CarbonEntryResponse)
async def create_carbon_entry(
    entry_data: CarbonEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new carbon footprint entry"""
    
    # Create new carbon entry
    db_entry = CarbonEntry(
        user_id=current_user.id,
        category=entry_data.category,
        activity=entry_data.activity,
        amount=entry_data.amount,
        unit=entry_data.unit,
        carbon_footprint=entry_data.carbon_footprint,
        location=entry_data.location,
        notes=entry_data.notes,
        verified=False  # Initially unverified
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return CarbonEntryResponse(
        id=db_entry.id,
        category=db_entry.category,
        activity=db_entry.activity,
        amount=db_entry.amount,
        unit=db_entry.unit,
        carbon_footprint=db_entry.carbon_footprint,
        location=db_entry.location,
        notes=db_entry.notes,
        verified=db_entry.verified,
        verification_source=db_entry.verification_source,
        created_at=db_entry.created_at
    )

@router.get("/entries", response_model=List[CarbonEntryResponse])
async def get_carbon_entries(
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    category: Optional[CarbonCategory] = Query(None, description="Category filter"),
    limit: int = Query(100, le=1000, description="Maximum number of entries"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get carbon footprint entries for the current user"""
    
    query = db.query(CarbonEntry).filter(CarbonEntry.user_id == current_user.id)
    
    # Apply filters
    if start_date:
        query = query.filter(CarbonEntry.created_at >= start_date)
    if end_date:
        query = query.filter(CarbonEntry.created_at <= end_date)
    if category:
        query = query.filter(CarbonEntry.category == category)
    
    # Order by creation date descending
    query = query.order_by(CarbonEntry.created_at.desc())
    
    # Apply pagination
    entries = query.offset(offset).limit(limit).all()
    
    return [
        CarbonEntryResponse(
            id=entry.id,
            category=entry.category,
            activity=entry.activity,
            amount=entry.amount,
            unit=entry.unit,
            carbon_footprint=entry.carbon_footprint,
            location=entry.location,
            notes=entry.notes,
            verified=entry.verified,
            verification_source=entry.verification_source,
            created_at=entry.created_at
        )
        for entry in entries
    ]

@router.get("/summary", response_model=CarbonSummary)
async def get_carbon_summary(
    period: str = Query("month", regex="^(day|week|month|year)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get carbon footprint summary for specified period"""
    
    now = datetime.now()
    
    # Calculate date range based on period
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # year
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get total carbon footprint for period
    total_result = db.query(func.sum(CarbonEntry.carbon_footprint)).filter(
        and_(
            CarbonEntry.user_id == current_user.id,
            CarbonEntry.created_at >= start_date
        )
    ).scalar()
    
    total_carbon = float(total_result) if total_result else 0.0
    
    # Get breakdown by category
    category_breakdown = db.query(
        CarbonEntry.category,
        func.sum(CarbonEntry.carbon_footprint).label('total')
    ).filter(
        and_(
            CarbonEntry.user_id == current_user.id,
            CarbonEntry.created_at >= start_date
        )
    ).group_by(CarbonEntry.category).all()
    
    breakdown = {
        category.value: 0.0 for category in CarbonCategory
    }
    
    for category, total in category_breakdown:
        breakdown[category.value] = float(total)
    
    # Calculate entry count
    entry_count = db.query(func.count(CarbonEntry.id)).filter(
        and_(
            CarbonEntry.user_id == current_user.id,
            CarbonEntry.created_at >= start_date
        )
    ).scalar()
    
    # Calculate average daily carbon
    if period == "day":
        avg_daily = total_carbon
    elif period == "week":
        days_in_period = 7
        avg_daily = total_carbon / days_in_period if days_in_period > 0 else 0
    elif period == "month":
        days_in_period = (now - start_date).days + 1
        avg_daily = total_carbon / days_in_period if days_in_period > 0 else 0
    else:  # year
        days_in_period = (now - start_date).days + 1
        avg_daily = total_carbon / days_in_period if days_in_period > 0 else 0
    
    return CarbonSummary(
        period=period,
        total_carbon=total_carbon,
        category_breakdown=breakdown,
        entry_count=entry_count,
        average_daily=avg_daily,
        start_date=start_date.date(),
        end_date=now.date()
    )

@router.get("/trends", response_model=List[CarbonTrend])
async def get_carbon_trends(
    period: str = Query("month", regex="^(day|week|month)$"),
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get carbon footprint trends over time"""
    
    now = datetime.now()
    start_date = now - timedelta(days=days)
    
    # Group by date and calculate daily totals
    if period == "day":
        date_format = func.date(CarbonEntry.created_at)
    elif period == "week":
        # Group by week (Monday as start)
        date_format = func.date_trunc('week', CarbonEntry.created_at)
    else:  # month
        date_format = func.date_trunc('month', CarbonEntry.created_at)
    
    trends = db.query(
        date_format.label('date'),
        func.sum(CarbonEntry.carbon_footprint).label('total_carbon'),
        func.count(CarbonEntry.id).label('entry_count')
    ).filter(
        and_(
            CarbonEntry.user_id == current_user.id,
            CarbonEntry.created_at >= start_date
        )
    ).group_by(date_format).order_by(date_format).all()
    
    return [
        CarbonTrend(
            date=trend.date,
            total_carbon=float(trend.total_carbon),
            entry_count=trend.entry_count
        )
        for trend in trends
    ]

@router.delete("/entries/{entry_id}")
async def delete_carbon_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a carbon footprint entry"""
    
    # Find the entry
    entry = db.query(CarbonEntry).filter(
        and_(
            CarbonEntry.id == entry_id,
            CarbonEntry.user_id == current_user.id
        )
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carbon entry not found"
        )
    
    db.delete(entry)
    db.commit()
    
    return {"message": "Carbon entry deleted successfully"}

@router.get("/goals", response_model=CarbonGoals)
async def get_carbon_goals(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get carbon footprint goals and progress"""
    
    # Get current year totals
    year_start = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    current_total = db.query(func.sum(CarbonEntry.carbon_footprint)).filter(
        and_(
            CarbonEntry.user_id == current_user.id,
            CarbonEntry.created_at >= year_start
        )
    ).scalar()
    
    current_total = float(current_total) if current_total else 0.0
    
    # Calculate progress
    progress_percentage = (current_total / current_user.carbon_goal * 100) if current_user.carbon_goal > 0 else 0
    
    # Calculate days remaining in year
    year_end = datetime(datetime.now().year, 12, 31)
    days_remaining = (year_end - datetime.now()).days
    
    # Calculate required daily average to meet goal
    if days_remaining > 0:
        remaining_budget = max(0, current_user.carbon_goal - current_total)
        required_daily_avg = remaining_budget / days_remaining
    else:
        required_daily_avg = 0
    
    return CarbonGoals(
        annual_goal=current_user.carbon_goal,
        current_total=current_total,
        progress_percentage=min(progress_percentage, 100),
        days_remaining=days_remaining,
        required_daily_average=required_daily_avg,
        on_track=progress_percentage <= 100
    )