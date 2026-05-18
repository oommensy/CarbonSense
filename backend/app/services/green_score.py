"""
Green Score Engine
Computes a 0–100 green score for AI inference pipelines and workloads.
Modelled after DORA metrics but for sustainability:
  - Energy Efficiency (30 pts): tokens/kWh vs hardware baseline
  - Carbon Intensity (25 pts): gCO2e/request vs regional average
  - Hardware Utilization (20 pts): avg GPU util vs idle waste
  - Optimization Level (15 pts): quantization, batching, caching
  - Carbon-Aware Scheduling (10 pts): % of runs in low-carbon windows
"""

from dataclasses import dataclass
from typing import Optional


# Baseline references (industry benchmarks)
BASELINE_TOKENS_PER_KWH = {
    "gpu_nvidia_a100": 2_500_000,
    "gpu_nvidia_h100": 4_000_000,
    "gpu_nvidia_v100": 1_200_000,
    "gpu_nvidia_t4":   800_000,
    "gpu_amd_mi300":   3_500_000,
    "npu_google_tpu":  5_000_000,
    "cpu_generic":     150_000,
    "edge_device":     300_000,
}

QUANTIZATION_SCORES = {
    "fp32": 0.0,
    "fp16": 0.4,
    "bf16": 0.4,
    "int8": 0.7,
    "int4": 0.9,
    "gguf": 0.85,
    None:   0.0,
}


@dataclass
class GreenScoreBreakdown:
    energy_efficiency:      float   # 0–30
    carbon_intensity:       float   # 0–25
    hardware_utilization:   float   # 0–20
    optimization_level:     float   # 0–15
    carbon_aware_scheduling: float  # 0–10
    total:                  float   # 0–100
    grade:                  str     # A+ / A / B / C / D / F
    summary:                str


def compute_green_score(
    hardware_type: str,
    tokens_per_kwh: Optional[float],
    carbon_g_per_request: Optional[float],
    avg_gpu_utilization_pct: Optional[float],
    quantization: Optional[str],
    avg_batch_size: Optional[float],
    carbon_aware_pct: Optional[float],   # % of runs scheduled in low-carbon windows
    grid_intensity_gco2e: Optional[float],
) -> GreenScoreBreakdown:

    # ── 1. Energy Efficiency (30 pts) ────────────────────────────────────────
    baseline = BASELINE_TOKENS_PER_KWH.get(hardware_type, 1_000_000)
    if tokens_per_kwh and baseline:
        ratio = min(tokens_per_kwh / baseline, 1.5)
        energy_score = min(ratio * 20, 30)
    else:
        energy_score = 10.0  # neutral if unknown

    # ── 2. Carbon Intensity (25 pts) ─────────────────────────────────────────
    # Target: <1g CO2e per request for LLM inference
    if carbon_g_per_request is not None:
        if carbon_g_per_request <= 0.5:
            carbon_score = 25.0
        elif carbon_g_per_request <= 1.0:
            carbon_score = 20.0
        elif carbon_g_per_request <= 5.0:
            carbon_score = 15.0
        elif carbon_g_per_request <= 20.0:
            carbon_score = 8.0
        else:
            carbon_score = 2.0
    elif grid_intensity_gco2e is not None:
        # Score based on grid alone if per-request unknown
        if grid_intensity_gco2e < 100:
            carbon_score = 22.0
        elif grid_intensity_gco2e < 250:
            carbon_score = 15.0
        elif grid_intensity_gco2e < 400:
            carbon_score = 10.0
        else:
            carbon_score = 5.0
    else:
        carbon_score = 10.0

    # ── 3. Hardware Utilization (20 pts) ─────────────────────────────────────
    if avg_gpu_utilization_pct is not None:
        util = avg_gpu_utilization_pct / 100.0
        if util >= 0.85:
            hw_score = 20.0
        elif util >= 0.70:
            hw_score = 16.0
        elif util >= 0.50:
            hw_score = 10.0
        elif util >= 0.30:
            hw_score = 5.0
        else:
            hw_score = 1.0
    else:
        hw_score = 8.0

    # ── 4. Optimization Level (15 pts) ───────────────────────────────────────
    quant_score = QUANTIZATION_SCORES.get(quantization, 0.0) * 8  # 0–8 pts
    batch_score = 0.0
    if avg_batch_size:
        if avg_batch_size >= 32:
            batch_score = 7.0
        elif avg_batch_size >= 16:
            batch_score = 5.0
        elif avg_batch_size >= 8:
            batch_score = 3.0
        elif avg_batch_size >= 2:
            batch_score = 1.5
    opt_score = min(quant_score + batch_score, 15.0)

    # ── 5. Carbon-Aware Scheduling (10 pts) ──────────────────────────────────
    if carbon_aware_pct is not None:
        sched_score = (carbon_aware_pct / 100.0) * 10
    else:
        sched_score = 0.0

    total = round(energy_score + carbon_score + hw_score + opt_score + sched_score, 1)

    if total >= 90:
        grade = "A+"
    elif total >= 80:
        grade = "A"
    elif total >= 70:
        grade = "B"
    elif total >= 55:
        grade = "C"
    elif total >= 40:
        grade = "D"
    else:
        grade = "F"

    summary = _build_summary(total, grade, energy_score, carbon_score, hw_score, opt_score, sched_score)

    return GreenScoreBreakdown(
        energy_efficiency=round(energy_score, 1),
        carbon_intensity=round(carbon_score, 1),
        hardware_utilization=round(hw_score, 1),
        optimization_level=round(opt_score, 1),
        carbon_aware_scheduling=round(sched_score, 1),
        total=total,
        grade=grade,
        summary=summary,
    )


def _build_summary(total, grade, e, c, h, o, s) -> str:
    weak = []
    if e < 15:
        weak.append("energy efficiency")
    if c < 12:
        weak.append("carbon intensity")
    if h < 10:
        weak.append("GPU utilization")
    if o < 7:
        weak.append("model optimization")
    if s < 5:
        weak.append("carbon-aware scheduling")

    if not weak:
        return f"Excellent pipeline health (Grade {grade}). All sustainability dimensions are performing well."
    return (
        f"Grade {grade} ({total}/100). "
        f"Primary improvement areas: {', '.join(weak)}."
    )
