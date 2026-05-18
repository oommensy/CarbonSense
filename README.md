# CarbonSense — AI Energy Observability Platform

> **The Datadog for AI sustainability.** Monitor GPU/NPU energy consumption, track carbon per inference, optimize models, and schedule workloads carbon-aware across regions.

[![CI](https://github.com/oommensy/CarbonSense/actions/workflows/ci.yml/badge.svg)](https://github.com/oommensy/CarbonSense/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev)

---

## What is CarbonSense?

CarbonSense is an **AI infrastructure observability platform** purpose-built for ML engineers and platform teams who need to understand the **energy, carbon, and cost footprint** of their inference workloads.

Think Datadog — but instead of latency and error rates, the primary metrics are:
- **gCO2e per inference request**
- **Wh per 1,000 tokens**
- **GPU utilization vs idle energy waste**
- **Green Score** (0-100 composite sustainability rating)

---

## Key Features

| Feature | Description |
|---|---|
| **GPU/NPU Telemetry** | Real-time power draw, utilization, temperature, and energy per workload |
| **Carbon per Inference** | Per-request carbon accounting using DEFRA 2024 / EPA 2023 emission factors |
| **Green Score Engine** | 0-100 composite score across 5 dimensions |
| **Energy vs Latency Pareto** | Scatter plot of all workload runs with Pareto frontier |
| **Model Optimization Recommendations** | Quantization, batching, right-sizing with projected savings |
| **Carbon-Aware Scheduling** | Real-time grid intensity for 7 regions |
| **Edge vs Cloud Analysis** | TCO comparison for edge vs cloud deployment |
| **Pipeline Inspector** | Per-pipeline green score history and recommendations |

---

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
DATABASE_URL="sqlite:///./carbonsense.db" uvicorn main:app --reload
```

API docs: `http://localhost:8000/docs`

### Dashboard

```bash
cd dashboard
pnpm install
VITE_API_URL="http://localhost:8000/api/v1" pnpm dev
```

Dashboard: `http://localhost:3000`

---

## Green Score Methodology

| Dimension | Weight | Metric |
|---|---|---|
| Energy Efficiency | 30 pts | tokens/kWh vs hardware baseline |
| Carbon Intensity | 25 pts | gCO2e/request vs industry target (<1g) |
| Hardware Utilization | 20 pts | avg GPU util vs idle waste threshold |
| Optimization Level | 15 pts | quantization (INT8/INT4) + batch size |
| Carbon-Aware Scheduling | 10 pts | % of runs in low-carbon windows |

Grades: **A+** (>=90) | **A** (>=80) | **B** (>=70) | **C** (>=55) | **D** (>=40) | **F** (<40)

---

## Architecture

```
CarbonSense/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/             # REST API endpoints
│   │   ├── models/             # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── green_score.py  # Green Score Engine
│   │   │   └── recommendations.py
│   │   └── utils/seed_data.py  # Demo data seeder
│   ├── tests/                  # pytest test suite
│   └── main.py                 # FastAPI app
├── dashboard/                  # React + Vite + Tailwind
│   └── src/
│       ├── App.tsx             # Full dashboard (5 tabs)
│       └── api.ts              # API client
└── .github/workflows/ci.yml    # GitHub Actions CI/CD
```

---

## Roadmap

- [ ] OpenTelemetry SDK agents (Python, Go, Node.js)
- [ ] Electricity Maps API for live grid data
- [ ] Prometheus / Grafana exporter
- [ ] Kubernetes operator for carbon-aware scheduling
- [ ] ISO 14064 audit trail export
- [ ] Slack / PagerDuty green score alerts

## License

MIT
