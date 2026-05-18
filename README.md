# CarbonSense v2 — AI Runtime Intelligence Platform

> **The only platform that correlates performance, energy, carbon, and safety in real time.**
> See exactly how every optimization decision affects all four dimensions — simultaneously.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev)

---

## What Is CarbonSense?

CarbonSense is an open-source AI observability platform for teams running LLMs and ML models in production. It answers the question no other tool answers:

> *"If I quantize this model to INT8, what happens to my carbon footprint — and what happens to my safety score?"*

Most tools track one dimension. CarbonSense tracks all four:

| Dimension | What It Tracks |
|---|---|
| **Performance** | Latency, throughput, token/s, GPU utilization, cost |
| **Energy** | kWh per inference, power draw, PUE, energy cost |
| **Carbon** | g CO₂e per request, grid intensity, carbon-aware scheduling |
| **Safety** | PII detection, injection attempts, toxicity, hallucination risk |

---

## The Core Innovation: Trade-off Intelligence

CarbonSense is the first platform to **correlate** optimization decisions with safety outcomes. Example insights it generates automatically:

- *"Switching FP16 → INT8 reduced carbon by 31% and latency by 18%, but safety score dropped 6.2 points and hallucination risk increased 14%."*
- *"Edge deployment reduced carbon by 43% with no statistically significant safety regression."*
- *"INT4 quantization caused a critical 14-point safety regression — not recommended for customer-facing pipelines."*

No other tool — not LangSmith, not Arize, not Datadog LLM Observability — shows you this.

---

## Quick Start

### Docker Compose (Recommended)

```bash
git clone https://github.com/oommensy/CarbonSense
cd CarbonSense
docker compose up --build
```

- **Dashboard:** http://localhost:5173
- **API docs:** http://localhost:8000/docs

### Python SDK

```bash
pip install carbonsense
```

```python
from carbonsense import monitor

# One line — tracks performance, energy, carbon, AND safety
monitor.track_llm(
    provider="openai",
    model="gpt-4",
    prompt=prompt,
    response=response,
    latency_ms=145,
    token_usage=350,
    quantization="int8",
)

# Or wrap your OpenAI client automatically
import openai
client = monitor.wrap_openai(openai.OpenAI())

# Context manager for full pipeline tracing
with monitor.trace("rag-pipeline", provider="openai", model="gpt-4") as t:
    t.set_prompt(user_query)
    response = my_rag_pipeline(user_query)
    t.set_response(response)
```

---

## Dashboard Pages

| Page | Description |
|---|---|
| **Overview** | Fleet-wide stats: carbon, energy, cost, green scores, top models |
| **Pareto Analysis** | Energy vs latency frontier — find the optimal operating point |
| **Pipelines** | Per-pipeline breakdown with optimization recommendations |
| **Carbon Grid** | Real-time grid intensity across 7 regions, carbon-aware scheduling |
| **Telemetry** | Live GPU metrics, power draw, utilization heatmaps |
| **Safety Monitor** | Real-time safety scores, PII incidents, injection attempts, live evaluator |
| **Trade-off Intelligence** | Scatter plots, correlation heatmaps, optimization impact insights |

---

## Comparison

| Feature | CarbonSense | LangSmith | Arize AI | Datadog LLM | CodeCarbon |
|---|---|---|---|---|---|
| LLM performance tracking | ✅ | ✅ | ✅ | ✅ | ❌ |
| Carbon per inference | ✅ | ❌ | ❌ | ❌ | ✅ |
| Safety evaluation (runtime) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Trade-off correlation | ✅ | ❌ | ❌ | ❌ | ❌ |
| Green Score grading | ✅ | ❌ | ❌ | ❌ | ❌ |
| Open source | ✅ | ❌ | ❌ | ❌ | ✅ |
| One-line SDK | ✅ | ✅ | ❌ | ❌ | ✅ |

---

## Architecture

```
CarbonSense/
├── backend/                  FastAPI backend
│   ├── app/
│   │   ├── api/v1/           REST API routes (workloads, safety, analytics, ...)
│   │   ├── models/           SQLAlchemy models (AIWorkload + SafetyEvent)
│   │   ├── services/         green_score · safety · correlation · recommendations
│   │   └── utils/            Seed data generator
│   └── main.py
├── dashboard/                React + TypeScript + Tailwind + Recharts
│   └── src/
│       ├── App.tsx           Main app (7 tabs)
│       ├── SafetyTab.tsx     Safety Monitor page
│       ├── TradeoffTab.tsx   Trade-off Intelligence page
│       └── api.ts            API client
├── sdk/                      Python SDK
│   └── carbonsense/
│       ├── __init__.py
│       └── monitor.py        track_llm · wrap_openai · trace()
└── docker-compose.yml
```

---

## Green Score Methodology

| Dimension | Weight | Metric |
|---|---|---|
| Energy Efficiency | 30 pts | tokens/kWh vs hardware baseline |
| Carbon Intensity | 25 pts | gCO2e/request vs industry target (<1g) |
| Hardware Utilization | 20 pts | avg GPU util vs idle waste threshold |
| Optimization Level | 15 pts | quantization (INT8/INT4) + batch size |
| Carbon-Aware Scheduling | 10 pts | % of runs in low-carbon windows |

Grades: **A+** (≥90) | **A** (≥80) | **B** (≥70) | **C** (≥55) | **D** (≥40) | **F** (<40)

---

## Roadmap

- [ ] OpenTelemetry SDK agents (Python, Go, Node.js)
- [ ] Electricity Maps API for live grid data
- [ ] Prometheus / Grafana exporter
- [ ] VS Code extension
- [ ] HuggingFace Hub integration (auto-generate model cards)
- [ ] EU AI Act compliance report export
- [ ] Kubernetes operator for carbon-aware scheduling

---

## License

Apache 2.0
