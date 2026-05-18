"""
Model Optimization Recommendations Engine
Analyses workload telemetry and generates actionable recommendations
for reducing energy consumption, carbon footprint, and cost.
"""

from typing import List, Dict, Any


def generate_recommendations(workload_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Given aggregated workload statistics, return a ranked list of recommendations.
    Each recommendation includes projected savings and confidence score.
    """
    recs = []

    quantization    = workload_stats.get("quantization")
    avg_batch       = workload_stats.get("avg_batch_size", 1)
    avg_gpu_util    = workload_stats.get("avg_gpu_utilization_pct", 50)
    model_params_b  = workload_stats.get("model_params_b", 7)
    deployment      = workload_stats.get("deployment", "cloud_aws")
    grid_intensity  = workload_stats.get("grid_intensity_gco2e", 386)
    avg_latency_ms  = workload_stats.get("avg_latency_ms", 500)
    carbon_aware_pct = workload_stats.get("carbon_aware_pct", 0)
    hardware_type   = workload_stats.get("hardware_type", "gpu_nvidia_a100")
    cost_per_hour   = workload_stats.get("cost_per_hour", 3.0)

    # ── Quantization ─────────────────────────────────────────────────────────
    if quantization in ("fp32", "fp16", None):
        recs.append({
            "rec_type": "quantization",
            "priority": "high",
            "title": "Switch to INT8 or INT4 Quantization",
            "description": (
                f"Your pipeline is running at {quantization or 'full precision (fp32)'}. "
                "Quantizing to INT8 reduces model memory footprint by ~50% and energy draw "
                "by 30–40% with minimal accuracy degradation on most LLM tasks."
            ),
            "rationale": (
                "NVIDIA TensorRT INT8 and llama.cpp GGUF Q4_K_M benchmarks show 35–45% "
                "energy reduction with <1% perplexity increase on standard benchmarks."
            ),
            "estimated_energy_saving_pct": 38.0,
            "estimated_carbon_saving_pct": 38.0,
            "estimated_cost_saving_usd": round(cost_per_hour * 24 * 30 * 0.35, 2),
            "estimated_latency_change_pct": -25.0,
            "confidence_score": 0.88,
            "action_steps": [
                "Export model to ONNX format",
                "Run TensorRT INT8 calibration with representative dataset",
                "Validate accuracy on held-out eval set (target: <1% degradation)",
                "Deploy quantized model to staging, A/B test latency and quality",
                "Promote to production and monitor green score improvement",
            ],
        })
    elif quantization == "int8":
        recs.append({
            "rec_type": "quantization",
            "priority": "medium",
            "title": "Consider INT4 / GGUF Q4_K_M for Further Compression",
            "description": (
                "You are already using INT8. Stepping down to INT4 (GGUF Q4_K_M) "
                "can yield an additional 20–25% energy reduction, especially beneficial "
                "for edge deployments or cost-sensitive batch workloads."
            ),
            "rationale": "Llama.cpp Q4_K_M shows ~22% lower energy vs INT8 on A100.",
            "estimated_energy_saving_pct": 22.0,
            "estimated_carbon_saving_pct": 22.0,
            "estimated_cost_saving_usd": round(cost_per_hour * 24 * 30 * 0.20, 2),
            "estimated_latency_change_pct": -10.0,
            "confidence_score": 0.72,
            "action_steps": [
                "Run GGUF Q4_K_M conversion using llama.cpp convert script",
                "Benchmark perplexity on domain-specific eval set",
                "Compare latency and throughput vs INT8 baseline",
            ],
        })

    # ── Batching ─────────────────────────────────────────────────────────────
    if avg_batch < 8:
        recs.append({
            "rec_type": "batching",
            "priority": "high" if avg_batch < 4 else "medium",
            "title": f"Increase Batch Size (currently avg {avg_batch:.1f})",
            "description": (
                f"Your average batch size of {avg_batch:.1f} leaves significant GPU capacity "
                "idle between requests. Continuous batching (vLLM PagedAttention) can "
                "consolidate requests and improve tokens/kWh by 2–4x."
            ),
            "rationale": (
                "GPU energy draw is largely fixed regardless of batch size. "
                "Doubling throughput at the same power draw halves carbon per token."
            ),
            "estimated_energy_saving_pct": min(40.0, (8 / max(avg_batch, 1) - 1) * 20),
            "estimated_carbon_saving_pct": min(40.0, (8 / max(avg_batch, 1) - 1) * 20),
            "estimated_cost_saving_usd": round(cost_per_hour * 24 * 30 * 0.30, 2),
            "estimated_latency_change_pct": 15.0,
            "confidence_score": 0.85,
            "action_steps": [
                "Switch inference server to vLLM with continuous batching enabled",
                "Set max_num_seqs=256 and max_num_batched_tokens=8192",
                "Monitor p99 latency — add autoscaling if SLA is breached",
                "Profile GPU utilization before/after (target: >80%)",
            ],
        })

    # ── GPU Utilization ───────────────────────────────────────────────────────
    if avg_gpu_util < 50:
        recs.append({
            "rec_type": "hardware_switch",
            "priority": "high",
            "title": f"Right-Size Hardware (GPU util at {avg_gpu_util:.0f}%)",
            "description": (
                f"Average GPU utilization of {avg_gpu_util:.0f}% indicates significant "
                "idle capacity. Consider downgrading to a smaller GPU tier or "
                "consolidating workloads onto fewer nodes."
            ),
            "rationale": (
                "An A100 at 30% utilization consumes ~250W idle overhead. "
                "Migrating to a T4 or consolidating 3 underutilized A100s into 1 "
                "can cut energy by 40–60%."
            ),
            "estimated_energy_saving_pct": 45.0,
            "estimated_carbon_saving_pct": 45.0,
            "estimated_cost_saving_usd": round(cost_per_hour * 24 * 30 * 0.40, 2),
            "estimated_latency_change_pct": 5.0,
            "confidence_score": 0.80,
            "action_steps": [
                "Profile peak vs average load over 7-day window",
                "Identify consolidation candidates (util <40% for >70% of time)",
                "Test workload on T4 or smaller instance type",
                "Implement autoscaling to scale to zero during off-peak hours",
            ],
        })

    # ── Region / Carbon-Aware Scheduling ─────────────────────────────────────
    if grid_intensity > 300 and carbon_aware_pct < 30:
        low_carbon_region = "EU North (Norway/Sweden, ~26 gCO2e/kWh)" if "us" in deployment else "US West (Pacific NW, ~210 gCO2e/kWh)"
        saving_pct = round((grid_intensity - 150) / grid_intensity * 100, 1)
        recs.append({
            "rec_type": "region_shift",
            "priority": "high",
            "title": f"Shift Batch Workloads to Low-Carbon Region",
            "description": (
                f"Your current grid intensity is {grid_intensity:.0f} gCO2e/kWh. "
                f"Routing non-latency-sensitive batch jobs to {low_carbon_region} "
                f"could reduce carbon emissions by up to {saving_pct}%."
            ),
            "rationale": (
                "Carbon-aware computing (Green Software Foundation pattern) routes "
                "deferrable workloads to times/regions with surplus renewable energy."
            ),
            "estimated_energy_saving_pct": 0.0,
            "estimated_carbon_saving_pct": saving_pct,
            "estimated_cost_saving_usd": 0.0,
            "estimated_latency_change_pct": 20.0,
            "confidence_score": 0.75,
            "action_steps": [
                "Classify workloads as latency-sensitive vs deferrable",
                "Integrate Electricity Maps API for real-time grid intensity",
                "Configure scheduler to prefer regions with intensity <150 gCO2e/kWh",
                "Set SLA window (e.g., complete within 4 hours) for batch jobs",
            ],
        })

    # ── Carbon-Aware Scheduling ───────────────────────────────────────────────
    if carbon_aware_pct < 20:
        recs.append({
            "rec_type": "scheduling",
            "priority": "medium",
            "title": "Enable Carbon-Aware Inference Scheduling",
            "description": (
                "Only {:.0f}% of your workloads are currently scheduled in low-carbon "
                "windows. Enabling time-shifting for batch jobs to align with renewable "
                "energy peaks can reduce carbon by 20–40% at zero additional cost."
            ).format(carbon_aware_pct),
            "rationale": (
                "Grid carbon intensity varies by 3–5x throughout the day. "
                "Scheduling batch inference during solar/wind peaks is the "
                "highest-ROI carbon reduction strategy available."
            ),
            "estimated_energy_saving_pct": 0.0,
            "estimated_carbon_saving_pct": 30.0,
            "estimated_cost_saving_usd": 0.0,
            "estimated_latency_change_pct": 0.0,
            "confidence_score": 0.82,
            "action_steps": [
                "Integrate CarbonSense Carbon-Aware Scheduler SDK",
                "Tag workloads with latency_class: realtime | batch | background",
                "Set carbon_threshold: 200 gCO2e/kWh for batch jobs",
                "Monitor scheduling_events table for carbon savings attribution",
            ],
        })

    # ── Edge Offload ──────────────────────────────────────────────────────────
    if model_params_b <= 7 and "cloud" in deployment:
        recs.append({
            "rec_type": "edge_offload",
            "priority": "medium",
            "title": f"Offload {model_params_b}B Model to Edge / On-Prem",
            "description": (
                f"At {model_params_b}B parameters, this model is small enough to run "
                "efficiently on modern edge hardware (Apple M-series, NVIDIA Jetson Orin, "
                "or on-prem GPU servers). Eliminating cloud data transfer and idle "
                "instance costs can reduce total cost by 50–70%."
            ),
            "rationale": (
                "Cloud GPU instances carry a ~3–5x cost premium over on-prem hardware "
                "amortized over 3 years. For models ≤13B parameters, edge inference "
                "is often both cheaper and lower-latency."
            ),
            "estimated_energy_saving_pct": 15.0,
            "estimated_carbon_saving_pct": 20.0,
            "estimated_cost_saving_usd": round(cost_per_hour * 24 * 30 * 0.55, 2),
            "estimated_latency_change_pct": -40.0,
            "confidence_score": 0.70,
            "action_steps": [
                "Benchmark model on target edge hardware (llama.cpp / Ollama)",
                "Measure p50/p99 latency vs cloud baseline",
                "Calculate 3-year TCO: edge hardware + power vs cloud spend",
                "Deploy with Ollama or llama.cpp server on edge node",
                "Use CarbonSense edge agent for telemetry collection",
            ],
        })

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recs.sort(key=lambda r: priority_order.get(r["priority"], 99))
    return recs


def edge_vs_cloud_analysis(
    model_params_b: float,
    monthly_requests: int,
    avg_tokens_per_request: int,
    cloud_cost_per_hour: float,
    cloud_grid_intensity: float,
    edge_tdp_watts: float = 15.0,
    edge_grid_intensity: float = 150.0,
    edge_hardware_cost_usd: float = 500.0,
    amortization_months: int = 36,
) -> Dict[str, Any]:
    """
    Compare edge vs cloud deployment for a given model and traffic profile.
    Returns cost, energy, carbon, and latency comparison.
    """
    # Cloud estimates
    # Assume 1 GPU-hour per ~500k tokens for 7B model, scaling linearly
    tokens_per_month = monthly_requests * avg_tokens_per_request
    gpu_hours_per_month = tokens_per_month / 500_000 * (model_params_b / 7)
    cloud_cost_monthly = gpu_hours_per_month * cloud_cost_per_hour
    cloud_energy_kwh = gpu_hours_per_month * 0.4  # ~400W A100
    cloud_carbon_kg = cloud_energy_kwh * cloud_grid_intensity / 1000

    # Edge estimates
    edge_hours_per_month = 24 * 30  # always-on
    edge_energy_kwh = (edge_tdp_watts / 1000) * edge_hours_per_month
    edge_carbon_kg = edge_energy_kwh * edge_grid_intensity / 1000
    edge_hw_monthly = edge_hardware_cost_usd / amortization_months
    edge_power_cost = edge_energy_kwh * 0.12  # $0.12/kWh
    edge_cost_monthly = edge_hw_monthly + edge_power_cost

    return {
        "cloud": {
            "monthly_cost_usd": round(cloud_cost_monthly, 2),
            "monthly_energy_kwh": round(cloud_energy_kwh, 2),
            "monthly_carbon_kg": round(cloud_carbon_kg, 2),
            "grid_intensity_gco2e": cloud_grid_intensity,
            "avg_latency_ms_estimate": 180,
        },
        "edge": {
            "monthly_cost_usd": round(edge_cost_monthly, 2),
            "monthly_energy_kwh": round(edge_energy_kwh, 2),
            "monthly_carbon_kg": round(edge_carbon_kg, 2),
            "grid_intensity_gco2e": edge_grid_intensity,
            "avg_latency_ms_estimate": 45,
            "hardware_cost_usd": edge_hardware_cost_usd,
            "amortization_months": amortization_months,
        },
        "comparison": {
            "cost_saving_edge_usd": round(cloud_cost_monthly - edge_cost_monthly, 2),
            "cost_saving_pct": round((cloud_cost_monthly - edge_cost_monthly) / max(cloud_cost_monthly, 0.01) * 100, 1),
            "carbon_saving_kg": round(cloud_carbon_kg - edge_carbon_kg, 2),
            "carbon_saving_pct": round((cloud_carbon_kg - edge_carbon_kg) / max(cloud_carbon_kg, 0.01) * 100, 1),
            "latency_improvement_pct": 75,
            "recommendation": "edge" if edge_cost_monthly < cloud_cost_monthly * 0.7 else "cloud",
        },
    }
