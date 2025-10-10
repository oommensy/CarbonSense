from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class UserRole(str, enum.Enum):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.INDIVIDUAL)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String)
    carbon_goal = Column(Float, default=1000.0)  # Annual carbon goal in kg CO2
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    carbon_entries = relationship("CarbonEntry", back_populates="user")
    challenge_participations = relationship("ChallengeParticipation", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    corporate_profile = relationship("CorporateProfile", back_populates="user", uselist=False)

class CarbonCategory(str, enum.Enum):
    TRANSPORT = "transport"
    ENERGY = "energy"
    FOOD = "food"
    WASTE = "waste"
    CONSUMPTION = "consumption"

class CarbonEntry(Base):
    __tablename__ = "carbon_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(SQLEnum(CarbonCategory), nullable=False)
    activity = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    carbon_footprint = Column(Float, nullable=False)  # kg CO2
    location = Column(String)  # Optional location
    notes = Column(Text)
    verified = Column(Boolean, default=False)
    verification_source = Column(String)  # IoT, satellite, manual, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="carbon_entries")

class ChallengeType(str, enum.Enum):
    INDIVIDUAL = "individual"
    COMMUNITY = "community"
    CORPORATE = "corporate"

class ChallengeStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    challenge_type = Column(SQLEnum(ChallengeType), nullable=False)
    target_reduction = Column(Float)  # Target CO2 reduction in kg
    duration_days = Column(Integer, default=30)
    points_reward = Column(Integer, default=100)
    status = Column(SQLEnum(ChallengeStatus), default=ChallengeStatus.ACTIVE)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    participations = relationship("ChallengeParticipation", back_populates="challenge")

class ParticipationStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class ChallengeParticipation(Base):
    __tablename__ = "challenge_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    status = Column(SQLEnum(ParticipationStatus), default=ParticipationStatus.ACTIVE)
    progress = Column(Float, default=0.0)  # Progress percentage
    carbon_saved = Column(Float, default=0.0)  # Actual CO2 saved
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="challenge_participations")
    challenge = relationship("Challenge", back_populates="participations")

class AchievementType(str, enum.Enum):
    MILESTONE = "milestone"
    STREAK = "streak"
    REDUCTION = "reduction"
    COMMUNITY = "community"

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    achievement_type = Column(SQLEnum(AchievementType), nullable=False)
    criteria = Column(Text)  # JSON string with criteria
    points = Column(Integer, default=50)
    icon_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

class CorporateProfile(Base):
    __tablename__ = "corporate_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String, nullable=False)
    industry = Column(String)
    employee_count = Column(Integer)
    annual_revenue = Column(Float)
    sustainability_goals = Column(Text)  # JSON string
    carbon_target = Column(Float)  # Annual target in tons CO2
    verification_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="corporate_profile")

class IoTDevice(Base):
    __tablename__ = "iot_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_type = Column(String, nullable=False)  # smart_meter, vehicle_tracker, etc.
    device_id = Column(String, unique=True, nullable=False)
    name = Column(String)
    location = Column(String)
    is_active = Column(Boolean, default=True)
    last_reading_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IoTReading(Base):
    __tablename__ = "iot_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("iot_devices.id"), nullable=False)
    reading_type = Column(String, nullable=False)  # energy, fuel, etc.
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    carbon_equivalent = Column(Float)  # Calculated CO2 equivalent
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(Text)  # JSON for additional data