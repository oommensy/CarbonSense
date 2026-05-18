"""
CarbonSense AI Runtime Intelligence SDK
========================================
Production-grade telemetry SDK for AI systems.

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
"""

from .monitor import Monitor

monitor = Monitor()

__all__ = ["monitor", "Monitor"]
__version__ = "0.1.0"
