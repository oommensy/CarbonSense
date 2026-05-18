You are a senior staff-level AI infrastructure architect and full-stack engineer.

Your task is to design and implement an MVP platform called:

“CarbonSense AI Runtime Intelligence”

The platform combines:
1. AI observability
2. Responsible AI monitoring
3. Sustainability telemetry
4. Runtime benchmarking
5. AI system reliability analytics

This is NOT a chatbot application.
This is an operational intelligence platform for AI systems.

The product should feel like:
- Datadog for AI systems
- LangSmith + Grafana + CodeCarbon + Guardrails combined
- Production-grade AI runtime monitoring

====================================================
CORE PRODUCT VISION
====================================================

The platform monitors AI systems in real time and correlates:

- latency
- throughput
- token usage
- energy consumption
- carbon estimation
- hallucination risk
- safety violations
- jailbreak attempts
- model drift
- optimization impacts
- runtime reliability

The key innovation:
CORRELATE optimization + sustainability + safety behavior together.

Example:
- INT8 quantization reduced latency by 40%
- but hallucination rate increased by 12%

The system should make these relationships visible.

====================================================
MVP REQUIREMENTS
====================================================

Build a modular, extensible architecture.

Tech stack:
- FastAPI backend
- React frontend (clean modern dashboard)
- PostgreSQL
- Redis (optional)
- Dockerized services
- OpenTelemetry support
- WebSocket live telemetry updates
- Grafana-compatible metrics if possible

Python version:
- Python 3.11+

Frontend:
- modern minimal observability UI
- dark mode inspired by Datadog/Grafana/Vercel
- highly visual dashboard

====================================================
CORE MODULES
====================================================

1. Runtime Telemetry SDK
2. AI Monitoring Backend
3. Safety Evaluation Engine
4. Sustainability Engine
5. Correlation Analytics
6. Dashboard UI
7. Benchmark Runner

====================================================
1. RUNTIME TELEMETRY SDK
====================================================

Create a Python SDK:

Example usage:

from carbonsense import monitor

monitor.track_llm(
    provider="openai",
    model="gpt-4",
    prompt=prompt,
    response=response,
    latency_ms=120,
    token_usage=350
)

monitor.track_energy(
    gpu_utilization=80,
    power_watts=220
)

monitor.track_agent(
    tool_calls=[...],
    iterations=4
)

SDK should support:
- OpenAI
- Anthropic
- Ollama
- HuggingFace
- local models
- vLLM
- OpenVINO

Architecture should allow future plugins.

====================================================
2. AI MONITORING BACKEND
====================================================

Backend responsibilities:
- ingest telemetry
- store metrics
- stream live updates
- expose APIs
- aggregate traces
- support multi-model monitoring

Create:
- REST APIs
- WebSocket telemetry streaming
- async ingestion pipeline

Track:
- latency
- TPS
- token usage
- model version
- request IDs
- deployment IDs
- edge/cloud source
- hardware type
- inference provider

====================================================
3. SAFETY EVALUATION ENGINE
====================================================

Implement lightweight runtime safety analysis.

Features:
- hallucination heuristics
- toxicity scoring
- jailbreak detection
- unsafe content classification
- prompt injection detection
- anomaly detection

Do NOT overcomplicate with heavy ML initially.
Use modular pluggable evaluators.

Output:
- risk scores
- severity levels
- event traces

====================================================
4. SUSTAINABILITY ENGINE
====================================================

Integrate:
- CodeCarbon
- GPU utilization tracking
- estimated energy per request
- carbon estimation
- efficiency scoring

Track:
- carbon/request
- energy/session
- watts/token
- inference efficiency
- model efficiency rankings

Support:
- cloud inference
- edge inference
- CPU/GPU/NPU environments

====================================================
5. CORRELATION ANALYTICS
====================================================

MOST IMPORTANT MODULE.

Create analytics that correlate:

- optimization vs hallucination
- quantization vs reliability
- latency vs safety
- throughput vs quality
- carbon vs accuracy
- batching vs drift

Build:
- comparison views
- trend graphs
- anomaly timelines
- optimization impact reports

Example:
“Quantized INT8 deployment reduced carbon by 31% but increased unsafe outputs by 8%.”

====================================================
6. DASHBOARD UI
====================================================

Create a modern observability dashboard.

Sections:
- System Overview
- Model Health
- Safety Monitor
- Sustainability Metrics
- Live Telemetry
- Runtime Traces
- Optimization Analytics
- Alerts & Incidents

Visualizations:
- latency graphs
- token heatmaps
- carbon charts
- hallucination trends
- live request traces
- anomaly spikes
- deployment comparisons

Add:
- filtering
- model comparison
- deployment comparison
- time ranges

====================================================
7. BENCHMARK RUNNER
====================================================

Implement benchmark workflows.

Allow users to:
- compare models
- compare quantization variants
- compare deployments
- compare edge vs cloud

Generate reports:
- latency
- throughput
- energy
- hallucination rate
- toxicity rate
- efficiency score

====================================================
ARCHITECTURE REQUIREMENTS
====================================================

Use:
- clean modular folder structure
- production-style architecture
- extensible plugin system
- typed Python
- pydantic models
- async APIs
- dependency injection where useful

Include:
- Docker setup
- docker-compose
- README
- architecture diagram
- API docs
- sample telemetry generator

====================================================
IMPORTANT PRODUCT DIRECTION
====================================================

This project should feel:
- infrastructure-grade
- systems-oriented
- observability-first
- engineering-heavy
- not like a toy AI wrapper

Avoid:
- generic chatbot UI
- superficial AI demos
- overfocus on prompting

Focus on:
- telemetry
- monitoring
- reliability
- governance
- sustainability
- benchmarking
- production operations

====================================================
DELIVERABLES
====================================================

Generate:
1. Full project architecture
2. Backend implementation
3. Frontend implementation
4. SDK implementation
5. Dockerized environment
6. Example dashboards
7. Sample telemetry simulations
8. README with setup instructions
9. Future roadmap section
10. Extensible plugin framework

The codebase should be clean enough to evolve into:
“Datadog for AI Systems.”
