from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, date
from app.models import CarbonCategory

class CarbonEntryCreate(BaseModel):
    category: CarbonCategory
    activity: str
    amount: float
    unit: str
    carbon_footprint: float
    location: Optional[str] = None
    notes: Optional[str] = None

class CarbonEntryResponse(BaseModel):
    id: int
    category: CarbonCategory
    activity: str
    amount: float
    unit: str
    carbon_footprint: float
    location: Optional[str] = None
    notes: Optional[str] = None
    verified: bool
    verification_source: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CarbonSummary(BaseModel):
    period: str
    total_carbon: float
    category_breakdown: Dict[str, float]
    entry_count: int
    average_daily: float
    start_date: date
    end_date: date

class CarbonGoals(BaseModel):
    annual_goal: float
    current_total: float
    progress_percentage: float
    days_remaining: int
    required_daily_average: float
    on_track: bool

class CarbonTrend(BaseModel):
    date: date
    total_carbon: float
    entry_count: int