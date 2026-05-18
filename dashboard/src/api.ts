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
