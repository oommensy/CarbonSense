"""
CarbonSense Data Models — AI Energy Observability Platform
Covers: AI workloads, GPU/NPU telemetry, inference runs, green scores, pipelines.
"""

import enum
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    Text, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class HardwareType(str, enum.Enum):
    GPU_NVIDIA_A100 = "gpu_nvidia_a100"
    GPU_NVIDIA_H100 = "gpu_nvidia_h100"
    GPU_NVIDIA_V100 = "gpu_nvidia_v100"
    GPU_NVIDIA_T4   = "gpu_nvidia_t4"
    GPU_AMD_MI300   = "gpu_amd_mi300"
    NPU_GOOGLE_TPU  = "npu_google_tpu"
    NPU_AWS_TRAINIUM = "npu_aws_trainium"
    NPU_APPLE_ANE   = "npu_apple_ane"
    CPU_GENERIC     = "cpu_generic"
    EDGE_DEVICE     = "edge_device"


class DeploymentTarget(str, enum.Enum):
    CLOUD_AWS       = "cloud_aws"
    CLOUD_GCP       = "cloud_gcp"
    CLOUD_AZURE     = "cloud_azure"
    EDGE_ON_PREM    = "edge_on_prem"
    EDGE_MOBILE     = "edge_mobile"
    EDGE_IOT        = "edge_iot"
    HYBRID          = "hybrid"


class ModelFramework(str, enum.Enum):
    PYTORCH     = "pytorch"
    TENSORFLOW  = "tensorflow"
    ONNX        = "onnx"
    TENSORRT    = "tensorrt"
    TRITON      = "triton"
    VLLM        = "vllm"
    OLLAMA      = "ollama"
    CUSTOM      = "custom"


class WorkloadType(str, enum.Enum):
    LLM_INFERENCE       = "llm_inference"
    LLM_TRAINING        = "llm_training"
    IMAGE_GENERATION    = "image_generation"
    EMBEDDING           = "embedding"
    CLASSIFICATION      = "classification"
    OBJECT_DETECTION    = "object_detection"
    SPEECH_TO_TEXT      = "speech_to_text"
    TEXT_TO_SPEECH      = "text_to_speech"
    FINE_TUNING         = "fine_tuning"
    BATCH_INFERENCE     = "batch_inference"


class GridRegion(str, enum.Enum):
    US_EAST         = "us_east"
    US_WEST         = "us_west"
    EU_WEST         = "eu_west"
    EU_NORTH        = "eu_north"
    ASIA_PACIFIC    = "asia_pacific"
    UK              = "uk"
    CANADA          = "canada"


# ─────────────────────────────────────────────────────────────────────────────
# Organization / Project
# ─────────────────────────────────────────────────────────────────────────────

class Organization(Base):
    __tablename__ = "organizations"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False, unique=True)
    slug        = Column(String, nullable=False, unique=True, index=True)
    api_key     = Column(String, unique=True, index=True)
    plan        = Column(String, default="free")   # free | pro | enterprise
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    projects    = relationship("Project", back_populates="org")
    users       = relationship("User", back_populates="org")


class Project(Base):
    __tablename__ = "projects"

    id          = Column(Integer, primary_key=True, index=True)
    org_id      = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name        = Column(String, nullable=False)
    description = Column(Text)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    org         = relationship("Organization", back_populates="projects")
    pipelines   = relationship("InferencePipeline", back_populates="project")
    workloads   = relationship("AIWorkload", back_populates="project")


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    org_id          = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    username        = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name       = Column(String)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    org             = relationship("Organization", back_populates="users")


# ─────────────────────────────────────────────────────────────────────────────
# Hardware Nodes
# ─────────────────────────────────────────────────────────────────────────────

class HardwareNode(Base):
    """Represents a physical or virtual compute node being monitored."""
    __tablename__ = "hardware_nodes"

    id              = Column(Integer, primary_key=True, index=True)
    org_id          = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name            = Column(String, nullable=False)
    hardware_type   = Column(SQLEnum(HardwareType), nullable=False)
    deployment      = Column(SQLEnum(DeploymentTarget), nullable=False)
    grid_region     = Column(SQLEnum(GridRegion), default=GridRegion.US_EAST)
    count           = Column(Integer, default=1)       # number of GPUs/NPUs
    tdp_watts       = Column(Float)                    # thermal design power per unit
    memory_gb       = Column(Float)
    location        = Column(String)
    cloud_instance  = Column(String)                   # e.g., "p4d.24xlarge"
    cost_per_hour   = Column(Float)                    # USD/hr
    is_active       = Column(Boolean, default=True)
    registered_at   = Column(DateTime(timezone=True), server_default=func.now())

    telemetry       = relationship("GPUTelemetry", back_populates="node")
    workloads       = relationship("AIWorkload", back_populates="node")


# ─────────────────────────────────────────────────────────────────────────────
# GPU / NPU Telemetry (time-series)
# ─────────────────────────────────────────────────────────────────────────────

class GPUTelemetry(Base):
    """Real-time or sampled GPU/NPU utilization and power metrics."""
    __tablename__ = "gpu_telemetry"

    id                  = Column(Integer, primary_key=True, index=True)
    node_id             = Column(Integer, ForeignKey("hardware_nodes.id"), nullable=False)
    workload_id         = Column(Integer, ForeignKey("ai_workloads.id"), nullable=True)
    timestamp           = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Utilization
    gpu_utilization_pct = Column(Float)    # 0–100
    memory_used_gb      = Column(Float)
    memory_total_gb     = Column(Float)
    memory_utilization_pct = Column(Float)

    # Power
    power_draw_watts    = Column(Float)    # instantaneous
    power_limit_watts   = Column(Float)
    temperature_c       = Column(Float)
    fan_speed_pct       = Column(Float)

    # Computed energy
    energy_kwh          = Column(Float)    # energy consumed in this sample window
    carbon_g_co2e       = Column(Float)    # grams CO2e for this window
    grid_intensity      = Column(Float)    # gCO2e/kWh at time of measurement

    # Throughput
    tokens_per_second   = Column(Float)
    requests_per_second = Column(Float)
    batch_size          = Column(Integer)

    node                = relationship("HardwareNode", back_populates="telemetry")
    workload            = relationship("AIWorkload", back_populates="telemetry")


# ─────────────────────────────────────────────────────────────────────────────
# AI Workloads
# ─────────────────────────────────────────────────────────────────────────────

class AIWorkload(Base):
    """A discrete AI job: training run, inference batch, fine-tune, etc."""
    __tablename__ = "ai_workloads"

    id                  = Column(Integer, primary_key=True, index=True)
    project_id          = Column(Integer, ForeignKey("projects.id"), nullable=False)
    node_id             = Column(Integer, ForeignKey("hardware_nodes.id"), nullable=True)
    pipeline_id         = Column(Integer, ForeignKey("inference_pipelines.id"), nullable=True)

    name                = Column(String, nullable=False)
    workload_type       = Column(SQLEnum(WorkloadType), nullable=False)
    model_name          = Column(String)          # e.g., "llama-3-70b", "stable-diffusion-xl"
    model_version       = Column(String)
    framework           = Column(SQLEnum(ModelFramework))
    model_params_b      = Column(Float)           # billions of parameters
    quantization        = Column(String)          # fp32, fp16, int8, int4, gguf

    # Timing
    started_at          = Column(DateTime(timezone=True))
    ended_at            = Column(DateTime(timezone=True))
    duration_seconds    = Column(Float)

    # Energy & Carbon
    total_energy_kwh    = Column(Float)
    total_carbon_g_co2e = Column(Float)
    avg_power_watts     = Column(Float)
    peak_power_watts    = Column(Float)
    pue_factor          = Column(Float, default=1.2)  # Power Usage Effectiveness

    # Performance
    total_tokens        = Column(Integer)
    total_requests      = Column(Integer)
    avg_latency_ms      = Column(Float)
    p99_latency_ms      = Column(Float)
    throughput_tps      = Column(Float)           # tokens per second

    # Cost
    compute_cost_usd    = Column(Float)
    energy_cost_usd     = Column(Float)
    cost_per_1k_tokens  = Column(Float)

    # Green Score (0–100)
    green_score         = Column(Float)
    green_score_breakdown = Column(JSON)

    status              = Column(String, default="running")  # running|completed|failed
    tags                = Column(JSON)
    metadata_           = Column("metadata", JSON)

    # ── Safety & RAI Scores (v2) ─────────────────────────────────────────────
    safety_score        = Column(Float)           # 0–100, higher = safer
    hallucination_risk  = Column(Float)           # 0–1 probability estimate
    toxicity_score      = Column(Float)           # 0–1
    pii_detected        = Column(Boolean, default=False)
    pii_count           = Column(Integer, default=0)
    injection_attempts  = Column(Integer, default=0)
    safety_violations   = Column(Integer, default=0)
    safety_events       = Column(JSON)            # list of safety event summaries

    project             = relationship("Project", back_populates="workloads")
    node                = relationship("HardwareNode", back_populates="workloads")
    telemetry           = relationship("GPUTelemetry", back_populates="workload")
    pipeline            = relationship("InferencePipeline", back_populates="workloads")
    safety_event_records = relationship("SafetyEvent", back_populates="workload")


# ─────────────────────────────────────────────────────────────────────────────
# Safety Events (v2 — RAI integration)
# ─────────────────────────────────────────────────────────────────────────────

class SafetyEventType(str, enum.Enum):
    PII_DETECTED        = "pii_detected"
    TOXICITY_FLAGGED    = "toxicity_flagged"
    INJECTION_ATTEMPT   = "injection_attempt"
    HALLUCINATION_RISK  = "hallucination_risk"
    UNSAFE_CONTENT      = "unsafe_content"
    ANOMALY             = "anomaly"

class SafetySeverity(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

class SafetyEvent(Base):
    """Individual safety violation or risk event tied to a workload."""
    __tablename__ = "safety_events"

    id              = Column(Integer, primary_key=True, index=True)
    workload_id     = Column(Integer, ForeignKey("ai_workloads.id"), nullable=False)
    pipeline_id     = Column(Integer, ForeignKey("inference_pipelines.id"), nullable=True)
    event_type      = Column(SQLEnum(SafetyEventType), nullable=False, index=True)
    severity        = Column(SQLEnum(SafetySeverity), default=SafetySeverity.MEDIUM)
    detail          = Column(Text)                # human-readable description
    score           = Column(Float)               # event-specific score (0–1)
    blocked         = Column(Boolean, default=False)
    metadata_       = Column("metadata", JSON)
    timestamp       = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    workload        = relationship("AIWorkload", back_populates="safety_event_records")


# ─────────────────────────────────────────────────────────────────────────────
# Inference Pipelines
# ─────────────────────────────────────────────────────────────────────────────

class InferencePipeline(Base):
    """A named inference pipeline (e.g., 'prod-chat-llama3', 'image-gen-sdxl')."""
    __tablename__ = "inference_pipelines"

    id                  = Column(Integer, primary_key=True, index=True)
    project_id          = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name                = Column(String, nullable=False)
    description         = Column(Text)
    model_name          = Column(String)
    framework           = Column(SQLEnum(ModelFramework))
    deployment          = Column(SQLEnum(DeploymentTarget))
    is_active           = Column(Boolean, default=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())

    # Aggregate green metrics (updated on each workload completion)
    current_green_score = Column(Float, default=0.0)
    total_energy_kwh    = Column(Float, default=0.0)
    total_carbon_kg     = Column(Float, default=0.0)
    total_requests      = Column(Integer, default=0)
    avg_latency_ms      = Column(Float)
    carbon_per_request_g = Column(Float)

    # ── Aggregate Safety Metrics (v2) ────────────────────────────────────────
    avg_safety_score        = Column(Float, default=100.0)
    total_safety_violations = Column(Integer, default=0)
    total_injection_attempts = Column(Integer, default=0)
    total_pii_incidents     = Column(Integer, default=0)

    project             = relationship("Project", back_populates="pipelines")
    workloads           = relationship("AIWorkload", back_populates="pipeline")
    recommendations     = relationship("OptimizationRecommendation", back_populates="pipeline")


# ─────────────────────────────────────────────────────────────────────────────
# Optimization Recommendations
# ─────────────────────────────────────────────────────────────────────────────

class RecommendationType(str, enum.Enum):
    QUANTIZATION        = "quantization"
    BATCHING            = "batching"
    HARDWARE_SWITCH     = "hardware_switch"
    REGION_SHIFT        = "region_shift"
    SCHEDULING          = "scheduling"
    MODEL_PRUNING       = "model_pruning"
    CACHING             = "caching"
    EDGE_OFFLOAD        = "edge_offload"
    CLOUD_MIGRATION     = "cloud_migration"


class RecommendationPriority(str, enum.Enum):
    CRITICAL    = "critical"
    HIGH        = "high"
    MEDIUM      = "medium"
    LOW         = "low"


class OptimizationRecommendation(Base):
    __tablename__ = "optimization_recommendations"

    id                  = Column(Integer, primary_key=True, index=True)
    pipeline_id         = Column(Integer, ForeignKey("inference_pipelines.id"), nullable=False)
    rec_type            = Column(SQLEnum(RecommendationType), nullable=False)
    priority            = Column(SQLEnum(RecommendationPriority), default=RecommendationPriority.MEDIUM)
    title               = Column(String, nullable=False)
    description         = Column(Text)
    rationale           = Column(Text)

    # Projected impact
    estimated_energy_saving_pct = Column(Float)   # % reduction in energy
    estimated_carbon_saving_pct = Column(Float)
    estimated_cost_saving_usd   = Column(Float)   # monthly
    estimated_latency_change_pct = Column(Float)  # negative = improvement
    confidence_score    = Column(Float)           # 0–1

    # Action
    action_steps        = Column(JSON)            # list of strings
    before_config       = Column(JSON)
    after_config        = Column(JSON)

    is_applied          = Column(Boolean, default=False)
    applied_at          = Column(DateTime(timezone=True))
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    pipeline            = relationship("InferencePipeline", back_populates="recommendations")


# ─────────────────────────────────────────────────────────────────────────────
# Carbon-Aware Scheduling Events
# ─────────────────────────────────────────────────────────────────────────────

class SchedulingEvent(Base):
    """Records when and why a workload was deferred/routed for carbon reasons."""
    __tablename__ = "scheduling_events"

    id                  = Column(Integer, primary_key=True, index=True)
    workload_id         = Column(Integer, ForeignKey("ai_workloads.id"), nullable=False)
    event_type          = Column(String)   # deferred | rerouted | cancelled | executed
    original_region     = Column(SQLEnum(GridRegion))
    selected_region     = Column(SQLEnum(GridRegion))
    original_intensity  = Column(Float)   # gCO2e/kWh
    selected_intensity  = Column(Float)
    carbon_saved_g      = Column(Float)
    reason              = Column(Text)
    timestamp           = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────────────────────────────────────────────────────────
# Grid Carbon Intensity (live / cached)
# ─────────────────────────────────────────────────────────────────────────────

class GridIntensitySnapshot(Base):
    __tablename__ = "grid_intensity_snapshots"

    id          = Column(Integer, primary_key=True, index=True)
    region      = Column(SQLEnum(GridRegion), nullable=False, index=True)
    intensity   = Column(Float, nullable=False)   # gCO2e/kWh
    source      = Column(String, default="electricitymap")
    renewable_pct = Column(Float)
    timestamp   = Column(DateTime(timezone=True), server_default=func.now(), index=True)
