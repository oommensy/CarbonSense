"""
CarbonSense Monitor SDK
========================
One-line telemetry for AI systems — tracks performance, energy, carbon,
and safety simultaneously on every LLM request.

Usage:
    from carbonsense import monitor

    monitor.track_llm(
        provider="openai",
        model="gpt-4",
        prompt=prompt,
        response=response,
        latency_ms=120,
        token_usage=350,
    )

    # Or use as a context manager:
    with monitor.trace("my-pipeline") as trace:
        response = openai_client.chat(prompt)
        trace.set_response(response)
"""

from __future__ import annotations

import os
import time
import json
import uuid
import threading
import logging
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Union

import httpx

logger = logging.getLogger("carbonsense")


# ─────────────────────────────────────────────────────────────────────────────
# Telemetry record
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LLMTelemetry:
    trace_id: str
    provider: str
    model: str
    prompt: Optional[str]
    response: Optional[str]
    latency_ms: float
    token_usage: int
    prompt_tokens: int
    completion_tokens: int
    quantization: Optional[str]
    deployment: Optional[str]
    pipeline_id: Optional[str]
    timestamp: str
    # Energy (estimated if not provided)
    energy_kwh: Optional[float]
    carbon_g: Optional[float]
    gpu_utilization_pct: Optional[float]
    power_watts: Optional[float]
    # Safety (auto-evaluated)
    safety_score: Optional[float]
    hallucination_risk: Optional[float]
    toxicity_score: Optional[float]
    pii_detected: Optional[bool]
    injection_attempts: Optional[int]
    safety_violations: Optional[int]
    safety_events: List[Dict] = field(default_factory=list)
    # Extra
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EnergyTelemetry:
    trace_id: str
    gpu_utilization_pct: float
    power_watts: float
    energy_kwh: float
    carbon_g: float
    duration_seconds: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentTelemetry:
    trace_id: str
    agent_name: Optional[str]
    tool_calls: List[Dict[str, Any]]
    iterations: int
    total_tokens: int
    total_latency_ms: float
    success: bool
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# Trace context manager
# ─────────────────────────────────────────────────────────────────────────────

class Trace:
    """Context manager for tracking a single LLM call."""

    def __init__(self, monitor: "Monitor", pipeline_name: str, **kwargs):
        self._monitor = monitor
        self._pipeline_name = pipeline_name
        self._kwargs = kwargs
        self._start = time.perf_counter()
        self._prompt: Optional[str] = None
        self._response: Optional[str] = None
        self._tokens: int = 0
        self.trace_id = str(uuid.uuid4())

    def set_prompt(self, prompt: str):
        self._prompt = prompt

    def set_response(self, response: str, tokens: int = 0):
        self._response = response
        self._tokens = tokens

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = (time.perf_counter() - self._start) * 1000
        self._monitor.track_llm(
            provider=self._kwargs.get("provider", "unknown"),
            model=self._kwargs.get("model", "unknown"),
            prompt=self._prompt,
            response=self._response,
            latency_ms=latency_ms,
            token_usage=self._tokens,
            pipeline_id=self._pipeline_name,
            **{k: v for k, v in self._kwargs.items() if k not in ("provider", "model")},
        )
        return False  # don't suppress exceptions


# ─────────────────────────────────────────────────────────────────────────────
# Energy estimator
# ─────────────────────────────────────────────────────────────────────────────

# Approximate energy per 1000 tokens by model size (kWh)
_ENERGY_PER_1K_TOKENS = {
    "70b":  0.00045,
    "13b":  0.00018,
    "8b":   0.00012,
    "7b":   0.00011,
    "6b":   0.00010,
    "3b":   0.00006,
    "1b":   0.00003,
    "default": 0.00020,
}

# Grid carbon intensity by region (gCO2e/kWh) — defaults
_GRID_INTENSITY = {
    "us_east": 386.0,
    "us_west": 210.0,
    "eu_west": 233.0,
    "eu_north": 26.0,
    "asia_pacific": 520.0,
    "default": 300.0,
}

def _estimate_energy(model: str, tokens: int, quantization: Optional[str]) -> float:
    """Estimate kWh for a given model and token count."""
    model_lower = model.lower()
    base = _ENERGY_PER_1K_TOKENS["default"]
    for size_key, val in _ENERGY_PER_1K_TOKENS.items():
        if size_key in model_lower:
            base = val
            break
    # Quantization efficiency factor
    quant_factor = 1.0
    if quantization:
        q = quantization.lower()
        if "int4" in q or "q4" in q or "gguf" in q:
            quant_factor = 0.55
        elif "int8" in q or "q8" in q:
            quant_factor = 0.70
        elif "fp16" in q:
            quant_factor = 0.85
    return base * (tokens / 1000) * quant_factor


def _estimate_carbon(energy_kwh: float, region: str = "default") -> float:
    intensity = _GRID_INTENSITY.get(region, _GRID_INTENSITY["default"])
    return energy_kwh * intensity


# ─────────────────────────────────────────────────────────────────────────────
# Safety evaluator (inline, no server dependency)
# ─────────────────────────────────────────────────────────────────────────────

def _run_safety_eval(prompt: Optional[str], response: Optional[str], quantization: Optional[str]) -> Dict[str, Any]:
    """Inline safety evaluation — runs locally without hitting the API."""
    try:
        import sys, os
        # Try to import from the backend services if available
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
        from app.services.safety import evaluate_workload
        result = evaluate_workload(prompt=prompt, response=response, quantization=quantization)
        return result.to_dict()
    except ImportError:
        pass

    # Fallback: minimal inline check
    import re
    _INJ = re.compile(r"ignore\s+(all\s+)?previous\s+instructions?|jailbreak|developer\s+mode", re.I)
    _PII = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\b\d{3}-\d{2}-\d{4}\b")

    combined = " ".join(filter(None, [prompt, response]))
    inj = len(_INJ.findall(combined))
    pii = len(_PII.findall(combined))
    safety = max(0.0, 100.0 - inj * 30 - pii * 15)

    return {
        "safety_score": safety,
        "hallucination_risk": 0.08 if quantization and "int4" in quantization.lower() else 0.04,
        "toxicity_score": 0.0,
        "pii_detected": pii > 0,
        "pii_count": pii,
        "injection_attempts": inj,
        "safety_violations": inj,
        "safety_events": [],
        "eval_ms": 0.0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main Monitor class
# ─────────────────────────────────────────────────────────────────────────────

class Monitor:
    """
    CarbonSense telemetry monitor.

    Tracks LLM calls, energy usage, and agent runs — automatically
    evaluating safety and estimating carbon on every request.

    Configuration via environment variables:
      CARBONSENSE_API_URL   — backend URL (default: http://localhost:8000)
      CARBONSENSE_API_KEY   — API key for authentication
      CARBONSENSE_REGION    — grid region for carbon estimation (default: us_east)
      CARBONSENSE_ASYNC     — send telemetry asynchronously (default: true)
      CARBONSENSE_SAFETY    — run safety evaluation (default: true)
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        region: Optional[str] = None,
        async_send: bool = True,
        run_safety: bool = True,
    ):
        self.api_url    = api_url or os.getenv("CARBONSENSE_API_URL", "http://localhost:8000")
        self.api_key    = api_key or os.getenv("CARBONSENSE_API_KEY", "")
        self.region     = region or os.getenv("CARBONSENSE_REGION", "us_east")
        self.async_send = async_send
        self.run_safety = run_safety
        self._session   = httpx.Client(timeout=5.0, headers={"X-API-Key": self.api_key})
        self._lock      = threading.Lock()

    # ── Public API ────────────────────────────────────────────────────────────

    def track_llm(
        self,
        provider: str,
        model: str,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        latency_ms: float = 0.0,
        token_usage: int = 0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        quantization: Optional[str] = None,
        deployment: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        energy_kwh: Optional[float] = None,
        carbon_g: Optional[float] = None,
        gpu_utilization_pct: Optional[float] = None,
        power_watts: Optional[float] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> LLMTelemetry:
        """
        Track a single LLM call. Automatically estimates energy, carbon,
        and runs safety evaluation.

        Returns the full telemetry record.
        """
        total_tokens = token_usage or (prompt_tokens + completion_tokens)

        # Energy estimation
        if energy_kwh is None:
            energy_kwh = _estimate_energy(model, total_tokens, quantization)
        if carbon_g is None:
            carbon_g = _estimate_carbon(energy_kwh, self.region)

        # Safety evaluation
        safety_data: Dict[str, Any] = {}
        if self.run_safety:
            safety_data = _run_safety_eval(prompt, response, quantization)

        record = LLMTelemetry(
            trace_id=str(uuid.uuid4()),
            provider=provider,
            model=model,
            prompt=prompt,
            response=response,
            latency_ms=latency_ms,
            token_usage=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            quantization=quantization,
            deployment=deployment,
            pipeline_id=pipeline_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            energy_kwh=energy_kwh,
            carbon_g=carbon_g,
            gpu_utilization_pct=gpu_utilization_pct,
            power_watts=power_watts,
            safety_score=safety_data.get("safety_score"),
            hallucination_risk=safety_data.get("hallucination_risk"),
            toxicity_score=safety_data.get("toxicity_score"),
            pii_detected=safety_data.get("pii_detected"),
            injection_attempts=safety_data.get("injection_attempts"),
            safety_violations=safety_data.get("safety_violations"),
            safety_events=safety_data.get("safety_events", []),
            tags=tags or {},
            metadata=kwargs,
        )

        self._send(record)
        return record

    def track_energy(
        self,
        gpu_utilization: float,
        power_watts: float,
        duration_seconds: float = 1.0,
        region: Optional[str] = None,
        **kwargs,
    ) -> EnergyTelemetry:
        """Track raw energy/GPU telemetry."""
        energy_kwh = (power_watts * duration_seconds) / 3_600_000
        carbon_g   = _estimate_carbon(energy_kwh, region or self.region)

        record = EnergyTelemetry(
            trace_id=str(uuid.uuid4()),
            gpu_utilization_pct=gpu_utilization,
            power_watts=power_watts,
            energy_kwh=energy_kwh,
            carbon_g=carbon_g,
            duration_seconds=duration_seconds,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=kwargs,
        )
        self._send(record, endpoint="/api/v1/telemetry/energy")
        return record

    def track_agent(
        self,
        tool_calls: List[Dict[str, Any]],
        iterations: int,
        total_tokens: int = 0,
        total_latency_ms: float = 0.0,
        agent_name: Optional[str] = None,
        success: bool = True,
        **kwargs,
    ) -> AgentTelemetry:
        """Track an agentic workflow run."""
        record = AgentTelemetry(
            trace_id=str(uuid.uuid4()),
            agent_name=agent_name,
            tool_calls=tool_calls,
            iterations=iterations,
            total_tokens=total_tokens,
            total_latency_ms=total_latency_ms,
            success=success,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=kwargs,
        )
        self._send(record, endpoint="/api/v1/telemetry/agent")
        return record

    def trace(self, pipeline_name: str, **kwargs) -> Trace:
        """Return a context manager for tracing a single LLM call."""
        return Trace(self, pipeline_name, **kwargs)

    # ── OpenAI wrapper ────────────────────────────────────────────────────────

    def wrap_openai(self, client: Any, pipeline_id: Optional[str] = None, **kwargs) -> Any:
        """
        Wrap an OpenAI client to automatically track all chat completions.

        Usage:
            import openai
            from carbonsense import monitor
            client = monitor.wrap_openai(openai.OpenAI(), pipeline_id="my-pipeline")
            response = client.chat.completions.create(...)  # automatically tracked
        """
        original_create = client.chat.completions.create

        def tracked_create(*args, **call_kwargs):
            t0 = time.perf_counter()
            result = original_create(*args, **call_kwargs)
            latency_ms = (time.perf_counter() - t0) * 1000

            model = call_kwargs.get("model", "unknown")
            messages = call_kwargs.get("messages", [])
            prompt = " ".join(m.get("content", "") for m in messages if m.get("role") != "assistant")
            response_text = ""
            total_tokens = 0

            if hasattr(result, "choices") and result.choices:
                response_text = result.choices[0].message.content or ""
            if hasattr(result, "usage") and result.usage:
                total_tokens = result.usage.total_tokens or 0

            self.track_llm(
                provider="openai",
                model=model,
                prompt=prompt[:500],
                response=response_text[:500],
                latency_ms=latency_ms,
                token_usage=total_tokens,
                pipeline_id=pipeline_id,
                **kwargs,
            )
            return result

        client.chat.completions.create = tracked_create
        return client

    # ── Private helpers ───────────────────────────────────────────────────────

    def _send(self, record: Any, endpoint: str = "/api/v1/telemetry/llm"):
        """Send telemetry to the CarbonSense backend."""
        if self.async_send:
            t = threading.Thread(target=self._post, args=(record, endpoint), daemon=True)
            t.start()
        else:
            self._post(record, endpoint)

    def _post(self, record: Any, endpoint: str):
        try:
            url = f"{self.api_url.rstrip('/')}{endpoint}"
            self._session.post(url, json=record.to_dict())
        except Exception as e:
            logger.debug(f"CarbonSense telemetry send failed (non-fatal): {e}")
