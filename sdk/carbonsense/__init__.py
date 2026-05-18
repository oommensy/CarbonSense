"""
CarbonSense AI Runtime Intelligence SDK
========================================
One-line telemetry for AI systems.
Tracks performance, energy, carbon, and safety simultaneously.

Quick start:
    from carbonsense import monitor
    monitor.track_llm(provider="openai", model="gpt-4", prompt=p, response=r, latency_ms=120, token_usage=350)

OpenAI auto-wrapping:
    client = monitor.wrap_openai(openai.OpenAI())

Context manager:
    with monitor.trace("my-pipeline", provider="openai", model="gpt-4") as t:
        t.set_prompt(user_input)
        response = my_llm(user_input)
        t.set_response(response)
"""

from .monitor import Monitor, LLMTelemetry, EnergyTelemetry, AgentTelemetry, Trace

# Module-level singleton — the primary interface
monitor = Monitor()

__all__ = ["monitor", "Monitor", "LLMTelemetry", "EnergyTelemetry", "AgentTelemetry", "Trace"]
__version__ = "0.2.0"
