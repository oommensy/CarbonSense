"""
CarbonSense Correlation Analytics Engine (v2)
==============================================
The core differentiator: correlates optimization decisions with their
simultaneous impact on safety, sustainability, and performance.

Surfaces insights like:
  "INT8 quantization reduced carbon by 31% but increased hallucination risk by 12%"
  "Batching to size 16 improved throughput 3x but safety score dropped 8 points"
  "Edge deployment cut energy 45% with no safety regression"

This is the module that makes CarbonSense unique vs. every other tool.
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.models import AIWorkload, InferencePipeline


# ─────────────────────────────────────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TradeoffInsight:
    """A single correlation insight between an optimization and its side effects."""
    title: str
    description: str
    optimization: str           # what changed (e.g., "quantization: fp16 → int8")
    carbon_change_pct: float    # negative = reduction
    energy_change_pct: float
    latency_change_pct: float   # negative = faster
    safety_change_pts: float    # change in safety_score (0–100 scale)
    hallucination_change_pct: float
    toxicity_change_pct: float
    cost_change_pct: float
    confidence: float           # 0–1
    severity: str               # "positive", "warning", "critical"
    recommendation: str
    sample_size: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CorrelationMatrix:
    """Pairwise correlations between key metrics."""
    pairs: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"pairs": self.pairs}


@dataclass
class OptimizationImpactReport:
    """Full trade-off analysis for a pipeline or model."""
    pipeline_id: Optional[int]
    model_name: Optional[str]
    generated_at: str
    insights: List[TradeoffInsight]
    correlation_matrix: CorrelationMatrix
    summary: str
    top_risk: Optional[str]
    top_opportunity: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "model_name": self.model_name,
            "generated_at": self.generated_at,
            "insights": [i.to_dict() for i in self.insights],
            "correlation_matrix": self.correlation_matrix.to_dict(),
            "summary": self.summary,
            "top_risk": self.top_risk,
            "top_opportunity": self.top_opportunity,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Analytics Engine
# ─────────────────────────────────────────────────────────────────────────────

class CorrelationEngine:
    """
    Analyses AIWorkload records to surface trade-off insights.
    Groups workloads by quantization, batch size, deployment type, etc.
    and computes deltas across sustainability + safety + performance dimensions.
    """

    def analyze_pipeline(
        self,
        pipeline_id: int,
        db: Session,
        days: int = 30,
    ) -> OptimizationImpactReport:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        workloads = (
            db.query(AIWorkload)
            .filter(AIWorkload.pipeline_id == pipeline_id)
            .filter(AIWorkload.started_at >= since)
            .filter(AIWorkload.status == "completed")
            .all()
        )
        pipeline = db.query(InferencePipeline).filter(InferencePipeline.id == pipeline_id).first()
        model_name = pipeline.model_name if pipeline else None
        return self._build_report(workloads, pipeline_id=pipeline_id, model_name=model_name)

    def analyze_model(
        self,
        model_name: str,
        db: Session,
        days: int = 30,
    ) -> OptimizationImpactReport:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        workloads = (
            db.query(AIWorkload)
            .filter(AIWorkload.model_name == model_name)
            .filter(AIWorkload.started_at >= since)
            .filter(AIWorkload.status == "completed")
            .all()
        )
        return self._build_report(workloads, pipeline_id=None, model_name=model_name)

    def global_summary(self, db: Session, days: int = 7) -> Dict[str, Any]:
        """Fast summary for the dashboard overview — no heavy computation."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        workloads = (
            db.query(AIWorkload)
            .filter(AIWorkload.started_at >= since)
            .filter(AIWorkload.status == "completed")
            .all()
        )
        if not workloads:
            return {"insights": [], "total_workloads": 0}

        insights = self._quantization_insights(workloads)
        insights += self._deployment_insights(workloads)
        insights += self._batch_insights(workloads)

        return {
            "total_workloads": len(workloads),
            "insights": [i.to_dict() for i in insights[:8]],
            "correlation_matrix": self._build_correlation_matrix(workloads).to_dict(),
        }

    # ── Private builders ─────────────────────────────────────────────────────

    def _build_report(
        self,
        workloads: List[AIWorkload],
        pipeline_id: Optional[int],
        model_name: Optional[str],
    ) -> OptimizationImpactReport:
        insights: List[TradeoffInsight] = []
        insights += self._quantization_insights(workloads)
        insights += self._deployment_insights(workloads)
        insights += self._batch_insights(workloads)

        matrix = self._build_correlation_matrix(workloads)
        summary = self._build_summary(insights, len(workloads))
        top_risk = next((i.title for i in insights if i.severity == "critical"), None)
        top_opp  = next((i.title for i in insights if i.severity == "positive"), None)

        return OptimizationImpactReport(
            pipeline_id=pipeline_id,
            model_name=model_name,
            generated_at=datetime.now(timezone.utc).isoformat(),
            insights=insights,
            correlation_matrix=matrix,
            summary=summary,
            top_risk=top_risk,
            top_opportunity=top_opp,
        )

    def _quantization_insights(self, workloads: List[AIWorkload]) -> List[TradeoffInsight]:
        """Compare workloads grouped by quantization level."""
        groups: Dict[str, List[AIWorkload]] = defaultdict(list)
        for w in workloads:
            if w.quantization:
                groups[w.quantization].append(w)

        if len(groups) < 2:
            return []

        insights = []
        quant_order = ["fp32", "fp16", "int8", "int4", "gguf"]
        sorted_groups = sorted(groups.items(), key=lambda x: quant_order.index(x[0]) if x[0] in quant_order else 99)

        for i in range(len(sorted_groups) - 1):
            base_key, base_wl = sorted_groups[i]
            comp_key, comp_wl = sorted_groups[i + 1]

            if len(base_wl) < 2 or len(comp_wl) < 2:
                continue

            b = _agg(base_wl)
            c = _agg(comp_wl)

            carbon_chg   = _pct_change(b["carbon"], c["carbon"])
            energy_chg   = _pct_change(b["energy"], c["energy"])
            latency_chg  = _pct_change(b["latency"], c["latency"])
            safety_chg   = (c["safety"] or 100) - (b["safety"] or 100)
            halluc_chg   = _pct_change(b["halluc"] or 0.1, c["halluc"] or 0.1)
            toxicity_chg = _pct_change(b["toxicity"] or 0.01, c["toxicity"] or 0.01)
            cost_chg     = _pct_change(b["cost"], c["cost"])

            # Determine severity
            if safety_chg < -10 or halluc_chg > 20:
                severity = "critical"
            elif safety_chg < -5 or halluc_chg > 10:
                severity = "warning"
            else:
                severity = "positive"

            desc = (
                f"Switching from {base_key.upper()} to {comp_key.upper()} "
                f"{'reduced' if carbon_chg < 0 else 'increased'} carbon by {abs(carbon_chg):.0f}% "
                f"and {'improved' if latency_chg < 0 else 'degraded'} latency by {abs(latency_chg):.0f}%"
            )
            if safety_chg != 0:
                desc += f", but safety score {'dropped' if safety_chg < 0 else 'improved'} by {abs(safety_chg):.1f} points"
            if halluc_chg > 5:
                desc += f" and hallucination risk increased {halluc_chg:.0f}%"

            rec = _quantization_recommendation(base_key, comp_key, carbon_chg, safety_chg, halluc_chg)

            insights.append(TradeoffInsight(
                title=f"Quantization: {base_key.upper()} → {comp_key.upper()}",
                description=desc,
                optimization=f"quantization:{base_key}→{comp_key}",
                carbon_change_pct=round(carbon_chg, 1),
                energy_change_pct=round(energy_chg, 1),
                latency_change_pct=round(latency_chg, 1),
                safety_change_pts=round(safety_chg, 1),
                hallucination_change_pct=round(halluc_chg, 1),
                toxicity_change_pct=round(toxicity_chg, 1),
                cost_change_pct=round(cost_chg, 1),
                confidence=min(0.95, 0.5 + min(len(base_wl), len(comp_wl)) * 0.05),
                severity=severity,
                recommendation=rec,
                sample_size=len(base_wl) + len(comp_wl),
            ))

        return insights

    def _deployment_insights(self, workloads: List[AIWorkload]) -> List[TradeoffInsight]:
        """Compare cloud vs edge deployments."""
        cloud = [w for w in workloads if w.node and "cloud" in (w.node.deployment.value if w.node.deployment else "")]
        edge  = [w for w in workloads if w.node and "edge" in (w.node.deployment.value if w.node.deployment else "")]

        if len(cloud) < 2 or len(edge) < 2:
            return []

        b, c = _agg(cloud), _agg(edge)
        carbon_chg  = _pct_change(b["carbon"], c["carbon"])
        energy_chg  = _pct_change(b["energy"], c["energy"])
        latency_chg = _pct_change(b["latency"], c["latency"])
        safety_chg  = (c["safety"] or 100) - (b["safety"] or 100)
        cost_chg    = _pct_change(b["cost"], c["cost"])

        severity = "positive" if carbon_chg < -20 and safety_chg > -5 else "warning"

        return [TradeoffInsight(
            title="Deployment: Cloud → Edge",
            description=(
                f"Edge inference {'reduced' if carbon_chg < 0 else 'increased'} carbon by {abs(carbon_chg):.0f}% "
                f"vs cloud. Latency {'improved' if latency_chg < 0 else 'degraded'} by {abs(latency_chg):.0f}%. "
                f"Safety score change: {safety_chg:+.1f} pts."
            ),
            optimization="deployment:cloud→edge",
            carbon_change_pct=round(carbon_chg, 1),
            energy_change_pct=round(energy_chg, 1),
            latency_change_pct=round(latency_chg, 1),
            safety_change_pts=round(safety_chg, 1),
            hallucination_change_pct=0.0,
            toxicity_change_pct=0.0,
            cost_change_pct=round(cost_chg, 1),
            confidence=min(0.9, 0.5 + min(len(cloud), len(edge)) * 0.04),
            severity=severity,
            recommendation=(
                "Edge deployment offers significant carbon savings. "
                "Monitor safety scores closely — edge models are often more quantized."
                if severity == "positive"
                else "Edge deployment shows safety regression. Validate model quality before full migration."
            ),
            sample_size=len(cloud) + len(edge),
        )]

    def _batch_insights(self, workloads: List[AIWorkload]) -> List[TradeoffInsight]:
        """Compare small vs large batch sizes."""
        # Use total_requests as a proxy for batch size
        sorted_wl = sorted([w for w in workloads if w.total_requests], key=lambda w: w.total_requests or 0)
        if len(sorted_wl) < 4:
            return []

        mid = len(sorted_wl) // 2
        small_batch = sorted_wl[:mid]
        large_batch = sorted_wl[mid:]

        b, c = _agg(small_batch), _agg(large_batch)
        carbon_chg  = _pct_change(b["carbon"], c["carbon"])
        latency_chg = _pct_change(b["latency"], c["latency"])
        safety_chg  = (c["safety"] or 100) - (b["safety"] or 100)

        if abs(carbon_chg) < 5 and abs(latency_chg) < 5:
            return []

        return [TradeoffInsight(
            title="Batching: Small → Large Batch",
            description=(
                f"Larger batches {'reduced' if carbon_chg < 0 else 'increased'} carbon/request by {abs(carbon_chg):.0f}% "
                f"and {'improved' if latency_chg < 0 else 'degraded'} throughput. "
                f"Safety score change: {safety_chg:+.1f} pts."
            ),
            optimization="batching:small→large",
            carbon_change_pct=round(carbon_chg, 1),
            energy_change_pct=round(carbon_chg * 0.9, 1),
            latency_change_pct=round(latency_chg, 1),
            safety_change_pts=round(safety_chg, 1),
            hallucination_change_pct=0.0,
            toxicity_change_pct=0.0,
            cost_change_pct=round(carbon_chg * 0.8, 1),
            confidence=0.7,
            severity="positive" if carbon_chg < -10 and safety_chg > -3 else "warning",
            recommendation=(
                "Increasing batch size improves efficiency. "
                "Ensure latency SLAs are still met for interactive workloads."
            ),
            sample_size=len(sorted_wl),
        )]

    def _build_correlation_matrix(self, workloads: List[AIWorkload]) -> CorrelationMatrix:
        """Compute pairwise Pearson correlations between key metrics."""
        metrics = {
            "carbon_g": [w.total_carbon_g_co2e or 0 for w in workloads],
            "latency_ms": [w.avg_latency_ms or 0 for w in workloads],
            "safety_score": [w.safety_score or 100 for w in workloads],
            "hallucination_risk": [w.hallucination_risk or 0 for w in workloads],
            "energy_kwh": [w.total_energy_kwh or 0 for w in workloads],
            "cost_usd": [w.compute_cost_usd or 0 for w in workloads],
        }

        pairs = []
        keys = list(metrics.keys())
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = metrics[keys[i]], metrics[keys[j]]
                r = _pearson(a, b)
                if r is not None:
                    pairs.append({
                        "x": keys[i],
                        "y": keys[j],
                        "correlation": round(r, 3),
                        "strength": "strong" if abs(r) > 0.7 else "moderate" if abs(r) > 0.4 else "weak",
                        "direction": "positive" if r > 0 else "negative",
                    })

        return CorrelationMatrix(pairs=sorted(pairs, key=lambda p: abs(p["correlation"]), reverse=True))

    def _build_summary(self, insights: List[TradeoffInsight], total_workloads: int) -> str:
        if not insights:
            return f"Analysed {total_workloads} workloads. No significant optimization trade-offs detected yet — more data needed."
        critical = [i for i in insights if i.severity == "critical"]
        positive = [i for i in insights if i.severity == "positive"]
        parts = [f"Analysed {total_workloads} workloads, found {len(insights)} trade-off insight(s)."]
        if critical:
            parts.append(f"⚠ {len(critical)} critical trade-off(s) require attention: {critical[0].title}.")
        if positive:
            parts.append(f"✓ {len(positive)} optimization opportunity(ies) identified: {positive[0].title}.")
        return " ".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _agg(workloads: List[AIWorkload]) -> Dict[str, float]:
    def mean(vals):
        vals = [v for v in vals if v is not None]
        return statistics.mean(vals) if vals else 0.0

    return {
        "carbon":   mean([w.total_carbon_g_co2e for w in workloads]),
        "energy":   mean([w.total_energy_kwh for w in workloads]),
        "latency":  mean([w.avg_latency_ms for w in workloads]),
        "safety":   mean([w.safety_score for w in workloads]),
        "halluc":   mean([w.hallucination_risk for w in workloads]),
        "toxicity": mean([w.toxicity_score for w in workloads]),
        "cost":     mean([w.compute_cost_usd for w in workloads]),
    }


def _pct_change(base: float, comp: float) -> float:
    if base == 0:
        return 0.0
    return ((comp - base) / base) * 100


def _pearson(x: List[float], y: List[float]) -> Optional[float]:
    n = len(x)
    if n < 3:
        return None
    try:
        mx, my = statistics.mean(x), statistics.mean(y)
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        den = (sum((xi - mx) ** 2 for xi in x) * sum((yi - my) ** 2 for yi in y)) ** 0.5
        return num / den if den != 0 else 0.0
    except Exception:
        return None


def _quantization_recommendation(base: str, comp: str, carbon_chg: float, safety_chg: float, halluc_chg: float) -> str:
    if safety_chg < -10 or halluc_chg > 20:
        return (
            f"Caution: {comp.upper()} quantization significantly degrades safety ({safety_chg:+.0f} pts). "
            "Run a full safety eval before deploying to production. Consider INT8 as a safer middle ground."
        )
    if carbon_chg < -20 and safety_chg > -5:
        return (
            f"{comp.upper()} quantization is a strong choice: {abs(carbon_chg):.0f}% carbon reduction "
            "with minimal safety impact. Recommended for production deployment."
        )
    return (
        f"{comp.upper()} offers moderate efficiency gains. Monitor safety scores and hallucination rates "
        "over the next 7 days before committing to full rollout."
    )


# Module-level singleton
engine = CorrelationEngine()
