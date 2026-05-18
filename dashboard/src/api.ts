import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'
const api = axios.create({ baseURL: API_BASE })

export const fetchWorkloadSummary = (days = 7) =>
  api.get(`/workloads/summary?days=${days}`).then(r => r.data)

export const fetchWorkloads = (days = 7) =>
  api.get(`/workloads/?days=${days}&limit=200`).then(r => r.data)

export const fetchWorkloadsByModel = (days = 7) =>
  api.get(`/workloads/by-model?days=${days}`).then(r => r.data)

export const fetchPareto = (days = 7) =>
  api.get(`/workloads/pareto?days=${days}`).then(r => r.data)

export const fetchPipelines = () =>
  api.get('/pipelines/').then(r => r.data)

export const fetchPipeline = (id: number) =>
  api.get(`/pipelines/${id}`).then(r => r.data)

export const fetchRecommendations = (pipelineId: number) =>
  api.get(`/pipelines/${pipelineId}/recommendations`).then(r => r.data)

export const fetchEdgeVsCloud = (pipelineId: number, monthlyRequests = 100000) =>
  api.get(`/pipelines/${pipelineId}/edge-vs-cloud?monthly_requests=${monthlyRequests}`).then(r => r.data)

export const fetchGridIntensity = () =>
  api.get('/carbon/intensity/current').then(r => r.data)

export const fetchGridHistory = (region = 'us_east', hours = 24) =>
  api.get(`/carbon/intensity/history?region=${region}&hours=${hours}`).then(r => r.data)

export const fetchTelemetrySummary = () =>
  api.get('/telemetry/summary').then(r => r.data)

export const fetchNodes = () =>
  api.get('/telemetry/nodes').then(r => r.data)

export const fetchLiveTelemetry = (limit = 50) =>
  api.get(`/telemetry/live?limit=${limit}`).then(r => r.data)

// ── Safety Monitor ──────────────────────────────────────────────────────────
export const fetchSafetySummary = (days = 7) =>
  api.get(`/safety/summary?days=${days}`).then(r => r.data)

export const fetchSafetyEvents = (days = 7, severity?: string, eventType?: string) => {
  let url = `/safety/events?days=${days}&limit=200`
  if (severity) url += `&severity=${severity}`
  if (eventType) url += `&event_type=${eventType}`
  return api.get(url).then(r => r.data)
}

export const fetchSafetyEventCounts = (days = 7) =>
  api.get(`/safety/events/counts?days=${days}`).then(r => r.data)

export const evaluateSafety = (payload: {
  prompt?: string; response?: string; model_name?: string; quantization?: string
}) => api.post('/safety/evaluate', payload).then(r => r.data)

// ── Trade-off Analytics ─────────────────────────────────────────────────────
export const fetchGlobalInsights = (days = 7) =>
  api.get(`/analytics/insights?days=${days}`).then(r => r.data)

export const fetchCorrelations = (days = 7) =>
  api.get(`/analytics/correlations?days=${days}`).then(r => r.data)

export const fetchScatterData = (x = 'total_carbon_g_co2e', y = 'safety_score', days = 7) =>
  api.get(`/analytics/scatter?x=${x}&y=${y}&days=${days}`).then(r => r.data)

export const fetchPipelineTradeoffs = (pipelineId: number, days = 30) =>
  api.get(`/analytics/pipeline/${pipelineId}/tradeoffs?days=${days}`).then(r => r.data)
