"""
Demo Data Seeder
Generates realistic AI workload telemetry for the CarbonSense demo dashboard.
"""

import random
import math
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.models import (
    Organization, Project, User, HardwareNode, AIWorkload, InferencePipeline,
    GPUTelemetry, OptimizationRecommendation, GridIntensitySnapshot,
    SchedulingEvent,
    HardwareType, DeploymentTarget, ModelFramework, WorkloadType,
    GridRegion, RecommendationType, RecommendationPriority
)
from app.services.green_score import compute_green_score
from app.services.recommendations import generate_recommendations
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

GRID_INTENSITIES = {
    GridRegion.US_EAST:      386.0,
    GridRegion.US_WEST:      210.0,
    GridRegion.EU_WEST:      233.0,
    GridRegion.EU_NORTH:     26.0,
    GridRegion.ASIA_PACIFIC: 520.0,
    GridRegion.UK:           207.0,
    GridRegion.CANADA:       130.0,
}

MODELS = [
    {"name": "llama-3-70b",       "params": 70,  "type": WorkloadType.LLM_INFERENCE,    "framework": ModelFramework.VLLM},
    {"name": "llama-3-8b",        "params": 8,   "type": WorkloadType.LLM_INFERENCE,    "framework": ModelFramework.VLLM},
    {"name": "gpt-j-6b",          "params": 6,   "type": WorkloadType.LLM_INFERENCE,    "framework": ModelFramework.PYTORCH},
    {"name": "stable-diffusion-xl","params": 3.5, "type": WorkloadType.IMAGE_GENERATION, "framework": ModelFramework.PYTORCH},
    {"name": "whisper-large-v3",  "params": 1.5, "type": WorkloadType.SPEECH_TO_TEXT,   "framework": ModelFramework.PYTORCH},
    {"name": "bge-large-en",      "params": 0.3, "type": WorkloadType.EMBEDDING,        "framework": ModelFramework.ONNX},
    {"name": "yolov8-x",          "params": 0.07,"type": WorkloadType.OBJECT_DETECTION, "framework": ModelFramework.TENSORRT},
]

HARDWARE_CONFIGS = [
    {"name": "prod-a100-cluster-1",  "hw": HardwareType.GPU_NVIDIA_A100, "deploy": DeploymentTarget.CLOUD_AWS,   "count": 8,  "tdp": 400, "mem": 80,  "instance": "p4d.24xlarge",  "cost": 32.77, "region": GridRegion.US_EAST},
    {"name": "prod-h100-cluster-1",  "hw": HardwareType.GPU_NVIDIA_H100, "deploy": DeploymentTarget.CLOUD_GCP,   "count": 4,  "tdp": 700, "mem": 80,  "instance": "a3-highgpu-8g", "cost": 28.50, "region": GridRegion.US_WEST},
    {"name": "dev-t4-pool",          "hw": HardwareType.GPU_NVIDIA_T4,   "deploy": DeploymentTarget.CLOUD_AWS,   "count": 4,  "tdp": 70,  "mem": 16,  "instance": "g4dn.12xlarge", "cost": 3.91,  "region": GridRegion.US_EAST},
    {"name": "edge-jetson-fleet",    "hw": HardwareType.EDGE_DEVICE,     "deploy": DeploymentTarget.EDGE_ON_PREM,"count": 12, "tdp": 15,  "mem": 16,  "instance": "Jetson Orin",   "cost": 0.08,  "region": GridRegion.EU_NORTH},
    {"name": "tpu-v4-pod",           "hw": HardwareType.NPU_GOOGLE_TPU,  "deploy": DeploymentTarget.CLOUD_GCP,   "count": 64, "tdp": 200, "mem": 32,  "instance": "tpu-v4-64",     "cost": 12.88, "region": GridRegion.EU_WEST},
]


def seed_all(db: Session):
    if db.query(Organization).first():
        return  # already seeded

    # Org + Users
    org = Organization(name="Acme AI Labs", slug="acme-ai", api_key="cs_demo_key_acme_2024", plan="enterprise")
    db.add(org)
    db.flush()

    user = User(
        org_id=org.id,
        email="demo@carbonsense.ai",
        username="demo",
        hashed_password=pwd_context.hash("demo1234"),
        full_name="Demo User",
        is_active=True,
    )
    db.add(user)

    project = Project(org_id=org.id, name="Production AI Platform", description="All production inference workloads")
    db.add(project)
    db.flush()

    # Hardware nodes
    nodes = []
    for cfg in HARDWARE_CONFIGS:
        node = HardwareNode(
            org_id=org.id,
            name=cfg["name"],
            hardware_type=cfg["hw"],
            deployment=cfg["deploy"],
            grid_region=cfg["region"],
            count=cfg["count"],
            tdp_watts=cfg["tdp"],
            memory_gb=cfg["mem"],
            cloud_instance=cfg["instance"],
            cost_per_hour=cfg["cost"],
        )
        db.add(node)
        nodes.append((node, cfg))
    db.flush()

    # Pipelines
    pipeline_configs = [
        {"name": "prod-chat-llama3-70b",  "model": "llama-3-70b",        "fw": ModelFramework.VLLM,    "deploy": DeploymentTarget.CLOUD_AWS},
        {"name": "prod-embeddings-bge",   "model": "bge-large-en",       "fw": ModelFramework.ONNX,    "deploy": DeploymentTarget.CLOUD_AWS},
        {"name": "prod-image-gen-sdxl",   "model": "stable-diffusion-xl","fw": ModelFramework.PYTORCH, "deploy": DeploymentTarget.CLOUD_GCP},
        {"name": "edge-detection-yolo",   "model": "yolov8-x",           "fw": ModelFramework.TENSORRT,"deploy": DeploymentTarget.EDGE_ON_PREM},
        {"name": "batch-whisper-stt",     "model": "whisper-large-v3",   "fw": ModelFramework.PYTORCH, "deploy": DeploymentTarget.CLOUD_AWS},
    ]
    pipelines = []
    for pc in pipeline_configs:
        p = InferencePipeline(
            project_id=project.id,
            name=pc["name"],
            model_name=pc["model"],
            framework=pc["fw"],
            deployment=pc["deploy"],
            is_active=True,
        )
        db.add(p)
        pipelines.append(p)
    db.flush()

    # Grid intensity snapshots (last 24h)
    now = datetime.now(timezone.utc)
    for region, base_intensity in GRID_INTENSITIES.items():
        for h in range(24):
            ts = now - timedelta(hours=h)
            variation = math.sin(h * math.pi / 12) * 0.15
            snap = GridIntensitySnapshot(
                region=region,
                intensity=round(base_intensity * (1 + variation + random.uniform(-0.05, 0.05)), 1),
                renewable_pct=round(random.uniform(20, 80), 1),
                timestamp=ts,
            )
            db.add(snap)

    # Workloads + Telemetry (last 7 days)
    quantizations = ["fp16", "int8", "int4", "fp32"]
    quant_weights = [0.3, 0.4, 0.2, 0.1]

    all_workloads = []
    for day in range(7):
        for _ in range(random.randint(8, 18)):
            model_cfg = random.choice(MODELS)
            node, node_cfg = random.choice(nodes)
            pipeline = random.choice(pipelines)
            quant = random.choices(quantizations, quant_weights)[0]

            start = now - timedelta(days=day, hours=random.uniform(0, 23))
            duration = random.uniform(300, 7200)
            end = start + timedelta(seconds=duration)

            grid_int = GRID_INTENSITIES[node.grid_region]
            avg_power = node.tdp_watts * random.uniform(0.55, 0.92)
            energy_kwh = (avg_power / 1000) * (duration / 3600)
            total_requests = int(random.uniform(500, 50000))
            tokens_per_req = random.randint(200, 2000)
            total_tokens = total_requests * tokens_per_req
            carbon_g = energy_kwh * grid_int

            avg_latency = random.uniform(50, 800)
            batch_size = random.uniform(1, 64)
            gpu_util = random.uniform(25, 95)

            score_data = compute_green_score(
                hardware_type=node.hardware_type.value,
                tokens_per_kwh=total_tokens / max(energy_kwh, 0.001),
                carbon_g_per_request=carbon_g / max(total_requests, 1),
                avg_gpu_utilization_pct=gpu_util,
                quantization=quant,
                avg_batch_size=batch_size,
                carbon_aware_pct=random.uniform(0, 60),
                grid_intensity_gco2e=grid_int,
            )

            wl = AIWorkload(
                project_id=project.id,
                node_id=node.id,
                pipeline_id=pipeline.id,
                name=f"{model_cfg['name']}-run-{random.randint(1000,9999)}",
                workload_type=model_cfg["type"],
                model_name=model_cfg["name"],
                model_version="1.0",
                framework=model_cfg["framework"],
                model_params_b=model_cfg["params"],
                quantization=quant,
                started_at=start,
                ended_at=end,
                duration_seconds=duration,
                total_energy_kwh=round(energy_kwh, 4),
                total_carbon_g_co2e=round(carbon_g, 2),
                avg_power_watts=round(avg_power, 1),
                peak_power_watts=round(avg_power * 1.15, 1),
                pue_factor=1.2,
                total_tokens=total_tokens,
                total_requests=total_requests,
                avg_latency_ms=round(avg_latency, 1),
                p99_latency_ms=round(avg_latency * 2.5, 1),
                throughput_tps=round(total_tokens / duration, 1),
                compute_cost_usd=round(node_cfg["cost"] * duration / 3600, 4),
                energy_cost_usd=round(energy_kwh * 0.12, 4),
                cost_per_1k_tokens=round((node_cfg["cost"] * duration / 3600) / (total_tokens / 1000), 6),
                green_score=score_data.total,
                green_score_breakdown={
                    "energy_efficiency": score_data.energy_efficiency,
                    "carbon_intensity": score_data.carbon_intensity,
                    "hardware_utilization": score_data.hardware_utilization,
                    "optimization_level": score_data.optimization_level,
                    "carbon_aware_scheduling": score_data.carbon_aware_scheduling,
                    "grade": score_data.grade,
                    "summary": score_data.summary,
                },
                status="completed",
                tags={"env": "production", "team": random.choice(["ml-platform", "search", "vision", "nlp"])},
                # Safety fields — degrade with lower quantization
                safety_score=round(max(0, min(100,
                    95 - (15 if quant == 'int4' else 7 if quant == 'int8' else 2 if quant == 'gguf' else 0)
                    + random.gauss(0, 4)
                )), 1),
                hallucination_risk=round(min(1.0, max(0,
                    (0.18 if quant == 'int4' else 0.10 if quant == 'int8' else 0.05)
                    + random.gauss(0, 0.02)
                )), 3),
                toxicity_score=round(max(0, random.gauss(0.03, 0.01)), 3),
                pii_detected=random.random() < 0.04,
                pii_count=random.randint(1, 3) if random.random() < 0.04 else 0,
                injection_attempts=random.randint(0, 2) if random.random() < 0.03 else 0,
                safety_violations=random.randint(0, 1) if random.random() < 0.05 else 0,
            )
            db.add(wl)
            all_workloads.append(wl)

    db.flush()

    # Telemetry samples for last 24h workloads
    recent_workloads = [w for w in all_workloads if w.started_at and w.started_at > now - timedelta(hours=24)]
    for wl in recent_workloads[:10]:
        for i in range(12):
            ts = wl.started_at + timedelta(minutes=i * 5)
            node = db.query(HardwareNode).filter(HardwareNode.id == wl.node_id).first()
            base_power = node.tdp_watts * random.uniform(0.5, 0.95) if node else 300
            sample = GPUTelemetry(
                node_id=wl.node_id,
                workload_id=wl.id,
                timestamp=ts,
                gpu_utilization_pct=round(random.uniform(40, 95), 1),
                memory_used_gb=round(random.uniform(20, 75), 1),
                memory_total_gb=80.0,
                memory_utilization_pct=round(random.uniform(25, 90), 1),
                power_draw_watts=round(base_power, 1),
                power_limit_watts=node.tdp_watts if node else 400,
                temperature_c=round(random.uniform(55, 82), 1),
                energy_kwh=round(base_power / 1000 * (5 / 60), 5),
                carbon_g_co2e=round(base_power / 1000 * (5 / 60) * GRID_INTENSITIES.get(node.grid_region if node else GridRegion.US_EAST, 386), 3),
                grid_intensity=GRID_INTENSITIES.get(node.grid_region if node else GridRegion.US_EAST, 386),
                tokens_per_second=round(random.uniform(100, 2000), 1),
                requests_per_second=round(random.uniform(1, 50), 2),
                batch_size=random.randint(4, 64),
            )
            db.add(sample)

    # Recommendations for first pipeline
    if pipelines:
        recs_data = generate_recommendations({
            "quantization": "fp16",
            "avg_batch_size": 4,
            "avg_gpu_utilization_pct": 42,
            "model_params_b": 70,
            "deployment": "cloud_aws",
            "grid_intensity_gco2e": 386,
            "avg_latency_ms": 320,
            "carbon_aware_pct": 5,
            "hardware_type": "gpu_nvidia_a100",
            "cost_per_hour": 32.77,
        })
        for rd in recs_data:
            rec = OptimizationRecommendation(
                pipeline_id=pipelines[0].id,
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
    print("✅ Demo data seeded successfully.")
