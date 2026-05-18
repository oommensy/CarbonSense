import { useState, useEffect } from 'react'
import {
  AreaChart, Area, BarChart, Bar, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell, ReferenceLine
} from 'recharts'
import {
  Cpu, Zap, Leaf, TrendingDown, Activity, BarChart2,
  Settings, Globe, RefreshCw, Server, GitBranch, Layers,
  ArrowUpRight, ArrowDownRight
} from 'lucide-react'
import {
  fetchWorkloadSummary, fetchWorkloadsByModel, fetchPareto,
  fetchPipelines, fetchGridIntensity, fetchTelemetrySummary,
  fetchNodes, fetchRecommendations, fetchEdgeVsCloud, fetchGridHistory
} from './api'

const cn = (...classes: (string | boolean | undefined)[]) =>
  classes.filter(Boolean).join(' ')

const fmt = (n: number | null | undefined, dec = 1) =>
  n == null ? '—' : n.toLocaleString(undefined, { maximumFractionDigits: dec })

const GREEN_GRADE_COLOR: Record<string, string> = {
  'A+': '#10b981', A: '#22c55e', B: '#84cc16',
  C: '#eab308', D: '#f97316', F: '#ef4444',
}

const PRIORITY_COLOR: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
}

const INTENSITY_COLOR = (v: number) => {
  if (v < 100) return '#10b981'
  if (v < 200) return '#22c55e'
  if (v < 350) return '#eab308'
  if (v < 500) return '#f97316'
  return '#ef4444'
}

function StatCard({ icon: Icon, label, value, sub, color = 'emerald', trend }: {
  icon: any; label: string; value: string; sub?: string; color?: string; trend?: number
}) {
  const colors: Record<string, string> = {
    emerald: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20',
    blue: 'from-blue-500/20 to-blue-600/5 border-blue-500/20',
    purple: 'from-purple-500/20 to-purple-600/5 border-purple-500/20',
    orange: 'from-orange-500/20 to-orange-600/5 border-orange-500/20',
    red: 'from-red-500/20 to-red-600/5 border-red-500/20',
  }
  const iconColors: Record<string, string> = {
    emerald: 'text-emerald-400', blue: 'text-blue-400',
    purple: 'text-purple-400', orange: 'text-orange-400', red: 'text-red-400',
  }
  return (
    <div className={cn('rounded-xl border bg-gradient-to-br p-5', colors[color])}>
      <div className="flex items-start justify-between mb-3">
        <Icon className={cn('w-5 h-5', iconColors[color])} />
        {trend != null && (
          <span className={cn('text-xs flex items-center gap-0.5', trend >= 0 ? 'text-emerald-400' : 'text-red-400')}>
            {trend >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-xs text-slate-400">{label}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  )
}

function GreenScoreRing({ score, grade, size = 80 }: { score: number; grade: string; size?: number }) {
  const r = size * 0.38
  const circ = 2 * Math.PI * r
  const dash = (score / 100) * circ
  const color = GREEN_GRADE_COLOR[grade] || '#94a3b8'
  return (
    <svg width={size} height={size} className="rotate-[-90deg]">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#1e293b" strokeWidth={size * 0.1} />
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color}
        strokeWidth={size * 0.1} strokeDasharray={`${dash} ${circ}`}
        strokeLinecap="round" style={{ transition: 'stroke-dasharray 0.8s ease' }} />
      <text x={size / 2} y={size / 2 + 1} textAnchor="middle" dominantBaseline="middle"
        fill={color} fontSize={size * 0.22} fontWeight="bold"
        style={{ transform: `rotate(90deg)`, transformOrigin: `${size / 2}px ${size / 2}px` }}>
        {grade}
      </text>
    </svg>
  )
}

function IntensityBadge({ rating }: { rating: string }) {
  const map: Record<string, string> = {
    excellent: 'bg-emerald-500/20 text-emerald-400',
    good: 'bg-green-500/20 text-green-400',
    moderate: 'bg-yellow-500/20 text-yellow-400',
    poor: 'bg-orange-500/20 text-orange-400',
    critical: 'bg-red-500/20 text-red-400',
  }
  return (
    <span className={cn('text-xs px-2 py-0.5 rounded-full font-medium capitalize', map[rating] || 'bg-slate-700 text-slate-400')}>
      {rating}
    </span>
  )
}

function OverviewTab() {
  const [summary, setSummary] = useState<any>(null)
  const [byModel, setByModel] = useState<any[]>([])
  const [telSummary, setTelSummary] = useState<any>(null)
  const [nodes, setNodes] = useState<any[]>([])

  useEffect(() => {
    fetchWorkloadSummary(7).then(setSummary)
    fetchWorkloadsByModel(7).then(setByModel)
    fetchTelemetrySummary().then(setTelSummary)
    fetchNodes().then(setNodes)
  }, [])

  const modelChartData = byModel.map(m => ({
    name: m.model?.replace('llama-3-', 'L3-').replace('stable-diffusion-xl', 'SDXL').replace('whisper-large-v3', 'Whisper').replace('bge-large-en', 'BGE').replace('yolov8-x', 'YOLOv8') || '?',
    energy: parseFloat((m.total_energy_kwh || 0).toFixed(2)),
    carbon: parseFloat(((m.total_carbon_kg || 0) * 1000).toFixed(1)),
    score: parseFloat((m.avg_green_score || 0).toFixed(1)),
    cost: parseFloat((m.total_cost_usd || 0).toFixed(2)),
  }))

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Activity} label="Total Runs (7d)" value={fmt(summary?.total_runs, 0)} color="blue" />
        <StatCard icon={Zap} label="Total Energy" value={`${fmt(summary?.total_energy_kwh)} kWh`} sub="7-day window" color="orange" />
        <StatCard icon={Leaf} label="Total Carbon" value={`${fmt(summary?.total_carbon_kg)} kg CO₂e`} sub="7-day window" color="emerald" />
        <StatCard icon={BarChart2} label="Avg Green Score" value={`${fmt(summary?.avg_green_score)}/100`} color="purple" />
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Cpu} label="Avg GPU Util" value={`${fmt(telSummary?.avg_gpu_utilization_pct)}%`} color="blue" />
        <StatCard icon={Activity} label="Avg Power Draw" value={`${fmt(telSummary?.avg_power_watts)} W`} color="orange" />
        <StatCard icon={TrendingDown} label="Avg Latency" value={`${fmt(summary?.avg_latency_ms)} ms`} color="purple" />
        <StatCard icon={Zap} label="Total Cost" value={`$${fmt(summary?.total_cost_usd, 0)}`} sub="7-day compute" color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">Energy by Model (kWh, 7d)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={modelChartData} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }} />
              <Bar dataKey="energy" fill="#10b981" radius={[4, 4, 0, 0]} name="Energy (kWh)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">Green Score by Model</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={modelChartData} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }} />
              <ReferenceLine y={80} stroke="#10b981" strokeDasharray="4 4" label={{ value: 'Target', fill: '#10b981', fontSize: 10 }} />
              <Bar dataKey="score" name="Green Score" radius={[4, 4, 0, 0]}>
                {modelChartData.map((entry, i) => (
                  <Cell key={i} fill={entry.score >= 80 ? '#10b981' : entry.score >= 60 ? '#eab308' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">Registered Hardware Nodes</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-400 text-xs border-b border-slate-700">
                <th className="text-left pb-2 pr-4">Node</th>
                <th className="text-left pb-2 pr-4">Hardware</th>
                <th className="text-left pb-2 pr-4">Deployment</th>
                <th className="text-left pb-2 pr-4">Region</th>
                <th className="text-right pb-2 pr-4">TDP (W)</th>
                <th className="text-right pb-2">$/hr</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((n: any) => (
                <tr key={n.id} className="border-b border-slate-700/40 hover:bg-slate-700/20">
                  <td className="py-2 pr-4 text-slate-200 font-medium">{n.name}</td>
                  <td className="py-2 pr-4 text-slate-400 text-xs">{n.hardware_type?.replace('gpu_nvidia_', 'NVIDIA ').replace('npu_google_tpu', 'Google TPU').replace('edge_device', 'Edge').toUpperCase()}</td>
                  <td className="py-2 pr-4 text-slate-400 text-xs capitalize">{n.deployment?.replace(/_/g, ' ')}</td>
                  <td className="py-2 pr-4 text-slate-400 text-xs capitalize">{n.grid_region?.replace(/_/g, ' ')}</td>
                  <td className="py-2 pr-4 text-right text-slate-300">{n.tdp_watts}</td>
                  <td className="py-2 text-right text-slate-300">${n.cost_per_hour}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function ParetoTab() {
  const [data, setData] = useState<any>({ points: [], pareto_frontier: [] })
  const [days, setDays] = useState(7)

  useEffect(() => { fetchPareto(days).then(setData) }, [days])

  const scatterData = data.points.map((p: any) => ({
    x: parseFloat((p.energy_wh_per_request || 0).toFixed(4)),
    y: parseFloat((p.latency_ms || 0).toFixed(0)),
    z: p.green_score || 50,
    name: p.model,
    quant: p.quantization,
  }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Energy vs Latency Pareto Frontier</h2>
          <p className="text-sm text-slate-400 mt-0.5">Each point is one workload run. Lower-left is optimal (less energy, less latency).</p>
        </div>
        <select value={days} onChange={e => setDays(+e.target.value)}
          className="bg-slate-800 border border-slate-700 text-slate-300 text-sm rounded-lg px-3 py-1.5">
          <option value={3}>Last 3 days</option>
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
        </select>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <div className="flex gap-4 mb-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" /> Green Score ≥ 80</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-yellow-500 inline-block" /> Score 60–79</span>
          <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-red-500 inline-block" /> Score &lt; 60</span>
        </div>
        <ResponsiveContainer width="100%" height={380}>
          <ScatterChart margin={{ top: 10, right: 30, bottom: 30, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="x" name="Energy (Wh/req)" type="number" tick={{ fill: '#94a3b8', fontSize: 11 }}
              label={{ value: 'Energy per Request (Wh)', position: 'insideBottom', offset: -15, fill: '#64748b', fontSize: 11 }} />
            <YAxis dataKey="y" name="Latency (ms)" type="number" tick={{ fill: '#94a3b8', fontSize: 11 }}
              label={{ value: 'Avg Latency (ms)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
            <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
              formatter={(val: any, name: any) => [
                name === 'Energy (Wh/req)' ? `${(+val).toFixed(4)} Wh` : `${(+val).toFixed(0)} ms`, name
              ]} />
            <Scatter name="Workloads" data={scatterData}
              shape={(props: any) => {
                const { cx, cy, payload } = props
                const score = payload.z || 50
                const color = score >= 80 ? '#10b981' : score >= 60 ? '#eab308' : '#ef4444'
                return <circle cx={cx} cy={cy} r={5} fill={color} fillOpacity={0.8} stroke={color} strokeWidth={1} />
              }} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">Pareto-Optimal Configurations ({data.pareto_frontier.length} found)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-400 text-xs border-b border-slate-700">
                <th className="text-left pb-2 pr-4">Model</th>
                <th className="text-left pb-2 pr-4">Quantization</th>
                <th className="text-left pb-2 pr-4">Hardware</th>
                <th className="text-right pb-2 pr-4">Energy (Wh/req)</th>
                <th className="text-right pb-2 pr-4">Latency (ms)</th>
                <th className="text-right pb-2 pr-4">Carbon (g/req)</th>
                <th className="text-right pb-2">Green Score</th>
              </tr>
            </thead>
            <tbody>
              {data.pareto_frontier.slice(0, 12).map((p: any, i: number) => (
                <tr key={i} className="border-b border-slate-700/40 hover:bg-slate-700/20">
                  <td className="py-2 pr-4 text-slate-200">{p.model}</td>
                  <td className="py-2 pr-4"><span className="bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded">{p.quantization || '—'}</span></td>
                  <td className="py-2 pr-4 text-slate-400 text-xs">{p.hardware?.replace('gpu_nvidia_', 'NVIDIA ').toUpperCase()}</td>
                  <td className="py-2 pr-4 text-right text-slate-300">{p.energy_wh_per_request?.toFixed(4)}</td>
                  <td className="py-2 pr-4 text-right text-slate-300">{p.latency_ms?.toFixed(0)}</td>
                  <td className="py-2 pr-4 text-right text-slate-300">{p.carbon_g_per_request?.toFixed(4)}</td>
                  <td className="py-2 text-right">
                    <span className={cn('text-xs font-bold', (p.green_score || 0) >= 80 ? 'text-emerald-400' : (p.green_score || 0) >= 60 ? 'text-yellow-400' : 'text-red-400')}>
                      {p.green_score?.toFixed(0) || '—'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function PipelinesTab() {
  const [pipelines, setPipelines] = useState<any[]>([])
  const [selected, setSelected] = useState<any>(null)
  const [recs, setRecs] = useState<any[]>([])
  const [edgeCloud, setEdgeCloud] = useState<any>(null)

  useEffect(() => { fetchPipelines().then(setPipelines) }, [])

  const selectPipeline = async (p: any) => {
    setSelected(p)
    const [r, ec] = await Promise.all([
      fetchRecommendations(p.id),
      fetchEdgeVsCloud(p.id),
    ])
    setRecs(r)
    setEdgeCloud(ec)
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-white">Inference Pipelines</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {pipelines.map((p: any) => {
          const score = p.avg_green_score || 0
          const grade = score >= 90 ? 'A+' : score >= 80 ? 'A' : score >= 70 ? 'B' : score >= 55 ? 'C' : 'D'
          return (
            <button key={p.id} onClick={() => selectPipeline(p)}
              className={cn('text-left bg-slate-800/60 border rounded-xl p-4 hover:border-emerald-500/50 transition-all',
                selected?.id === p.id ? 'border-emerald-500/70 ring-1 ring-emerald-500/30' : 'border-slate-700/50')}>
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="text-sm font-semibold text-slate-200">{p.name}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{p.model_name}</div>
                </div>
                <GreenScoreRing score={score} grade={grade} size={52} />
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div><span className="text-slate-500">Runs (7d)</span><div className="text-slate-300 font-medium">{p.runs_7d}</div></div>
                <div><span className="text-slate-500">Avg Latency</span><div className="text-slate-300 font-medium">{fmt(p.avg_latency_ms)} ms</div></div>
                <div><span className="text-slate-500">Energy</span><div className="text-slate-300 font-medium">{fmt(p.total_energy_kwh_7d)} kWh</div></div>
                <div><span className="text-slate-500">Carbon</span><div className="text-slate-300 font-medium">{fmt(p.total_carbon_kg_7d, 3)} kg</div></div>
              </div>
            </button>
          )
        })}
      </div>

      {selected && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
            <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <Settings className="w-4 h-4 text-emerald-400" />
              Optimization Recommendations — {selected.name}
            </h3>
            <div className="space-y-3">
              {recs.length === 0 && <p className="text-slate-500 text-sm">No recommendations available.</p>}
              {recs.map((r: any) => (
                <div key={r.id} className="border border-slate-700/50 rounded-lg p-3">
                  <div className="flex items-start justify-between mb-1">
                    <span className="text-sm font-medium text-slate-200">{r.title}</span>
                    <span className={cn('text-xs px-2 py-0.5 rounded-full border font-medium capitalize ml-2 shrink-0', PRIORITY_COLOR[r.priority] || '')}>{r.priority}</span>
                  </div>
                  <p className="text-xs text-slate-400 mb-2 line-clamp-2">{r.description}</p>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="bg-emerald-500/10 rounded p-1.5 text-center">
                      <div className="text-emerald-400 font-bold">-{r.estimated_carbon_saving_pct?.toFixed(0)}%</div>
                      <div className="text-slate-500">Carbon</div>
                    </div>
                    <div className="bg-blue-500/10 rounded p-1.5 text-center">
                      <div className="text-blue-400 font-bold">-{r.estimated_energy_saving_pct?.toFixed(0)}%</div>
                      <div className="text-slate-500">Energy</div>
                    </div>
                    <div className="bg-purple-500/10 rounded p-1.5 text-center">
                      <div className="text-purple-400 font-bold">${r.estimated_cost_saving_usd?.toFixed(0)}/mo</div>
                      <div className="text-slate-500">Savings</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {edgeCloud && (
            <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
              <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <Layers className="w-4 h-4 text-blue-400" />
                Edge vs Cloud Analysis
              </h3>
              <div className="grid grid-cols-2 gap-4 mb-4">
                {['cloud', 'edge'].map(type => {
                  const d = edgeCloud[type]
                  const isRec = edgeCloud.comparison?.recommendation === type
                  return (
                    <div key={type} className={cn('rounded-lg p-3 border', isRec ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-slate-700/50 bg-slate-900/40')}>
                      <div className="flex items-center gap-1.5 mb-2">
                        {type === 'cloud' ? <Server className="w-3.5 h-3.5 text-blue-400" /> : <Cpu className="w-3.5 h-3.5 text-purple-400" />}
                        <span className="text-xs font-semibold text-slate-200 capitalize">{type}</span>
                        {isRec && <span className="text-xs text-emerald-400 ml-auto">✓ Recommended</span>}
                      </div>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between"><span className="text-slate-500">Monthly Cost</span><span className="text-slate-300">${fmt(d.monthly_cost_usd)}</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Energy</span><span className="text-slate-300">{fmt(d.monthly_energy_kwh)} kWh</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Carbon</span><span className="text-slate-300">{fmt(d.monthly_carbon_kg)} kg</span></div>
                        <div className="flex justify-between"><span className="text-slate-500">Est. Latency</span><span className="text-slate-300">{d.avg_latency_ms_estimate} ms</span></div>
                      </div>
                    </div>
                  )
                })}
              </div>
              <div className="bg-slate-900/60 rounded-lg p-3 text-xs space-y-1">
                <div className="flex justify-between"><span className="text-slate-400">Cost Saving (Edge)</span><span className="text-emerald-400 font-medium">${fmt(edgeCloud.comparison?.cost_saving_edge_usd)}/mo ({fmt(edgeCloud.comparison?.cost_saving_pct)}%)</span></div>
                <div className="flex justify-between"><span className="text-slate-400">Carbon Saving</span><span className="text-emerald-400 font-medium">{fmt(edgeCloud.comparison?.carbon_saving_kg)} kg/mo</span></div>
                <div className="flex justify-between"><span className="text-slate-400">Latency Improvement</span><span className="text-blue-400 font-medium">{edgeCloud.comparison?.latency_improvement_pct}% faster</span></div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function CarbonGridTab() {
  const [regions, setRegions] = useState<any[]>([])
  const [history, setHistory] = useState<any[]>([])
  const [selectedRegion, setSelectedRegion] = useState('us_east')

  useEffect(() => { fetchGridIntensity().then(setRegions) }, [])
  useEffect(() => {
    fetchGridHistory(selectedRegion, 24).then(d => {
      setHistory(d.map((s: any) => ({
        time: new Date(s.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intensity: s.intensity,
        renewable: s.renewable_pct,
      })))
    })
  }, [selectedRegion])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-white">Live Grid Carbon Intensity</h2>
        <p className="text-sm text-slate-400 mt-0.5">Real-time gCO₂e/kWh by region. Schedule batch workloads in green windows.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {regions.map((r: any) => (
          <button key={r.region} onClick={() => setSelectedRegion(r.region)}
            className={cn('rounded-xl border p-3 text-left transition-all hover:border-emerald-500/50',
              selectedRegion === r.region ? 'border-emerald-500/70 bg-emerald-500/5' : 'border-slate-700/50 bg-slate-800/60')}>
            <div className="text-xs text-slate-500 mb-1 truncate">{r.label}</div>
            <div className="text-xl font-bold" style={{ color: INTENSITY_COLOR(r.intensity_gco2e_kwh || 999) }}>
              {r.intensity_gco2e_kwh?.toFixed(0) || '—'}
            </div>
            <div className="text-xs text-slate-500">gCO₂e/kWh</div>
            <div className="mt-1.5"><IntensityBadge rating={r.rating} /></div>
          </button>
        ))}
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">
          24h Intensity History — {regions.find(r => r.region === selectedRegion)?.label || selectedRegion}
        </h3>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={history} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="intensityGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 10 }} interval={3} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
            <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }} />
            <Area type="monotone" dataKey="intensity" stroke="#10b981" fill="url(#intensityGrad)" name="gCO₂e/kWh" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
          <Globe className="w-4 h-4 text-emerald-400" />
          Carbon-Aware Scheduling Advisor
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4">
            <div className="text-xs text-emerald-400 font-semibold mb-1">BEST REGION NOW</div>
            <div className="text-lg font-bold text-white">{regions[0]?.label || '—'}</div>
            <div className="text-sm text-emerald-400">{regions[0]?.intensity_gco2e_kwh?.toFixed(0)} gCO₂e/kWh</div>
            <div className="text-xs text-slate-400 mt-1">Schedule batch jobs here for lowest carbon impact</div>
          </div>
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
            <div className="text-xs text-yellow-400 font-semibold mb-1">AVOID NOW</div>
            <div className="text-lg font-bold text-white">{regions[regions.length - 1]?.label || '—'}</div>
            <div className="text-sm text-yellow-400">{regions[regions.length - 1]?.intensity_gco2e_kwh?.toFixed(0)} gCO₂e/kWh</div>
            <div className="text-xs text-slate-400 mt-1">Defer non-urgent workloads from this region</div>
          </div>
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
            <div className="text-xs text-blue-400 font-semibold mb-1">POTENTIAL SAVING</div>
            <div className="text-lg font-bold text-white">
              {regions.length >= 2
                ? `${(((regions[regions.length - 1]?.intensity_gco2e_kwh || 0) - (regions[0]?.intensity_gco2e_kwh || 0)) / (regions[regions.length - 1]?.intensity_gco2e_kwh || 1) * 100).toFixed(0)}%`
                : '—'}
            </div>
            <div className="text-sm text-blue-400">Carbon reduction</div>
            <div className="text-xs text-slate-400 mt-1">By routing from worst to best region</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function TelemetryTab() {
  const [telSummary, setTelSummary] = useState<any>(null)
  const [nodes, setNodes] = useState<any[]>([])

  useEffect(() => {
    fetchTelemetrySummary().then(setTelSummary)
    fetchNodes().then(setNodes)
  }, [])

  const nodeChartData = nodes.map(n => ({
    name: n.name?.split('-').slice(0, 2).join('-') || n.name,
    tdp: n.tdp_watts,
    cost: n.cost_per_hour,
    mem: n.memory_gb,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-white">GPU / NPU Telemetry</h2>
        <p className="text-sm text-slate-400 mt-0.5">Real-time hardware utilization, power draw, and energy metrics.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Cpu} label="Avg GPU Utilization" value={`${fmt(telSummary?.avg_gpu_utilization_pct)}%`} color="blue" />
        <StatCard icon={Zap} label="Avg Power Draw" value={`${fmt(telSummary?.avg_power_watts)} W`} color="orange" />
        <StatCard icon={Activity} label="Total Energy (24h)" value={`${fmt(telSummary?.total_energy_kwh, 3)} kWh`} color="purple" />
        <StatCard icon={Leaf} label="Total Carbon (24h)" value={`${fmt((telSummary?.total_carbon_g_co2e || 0) / 1000, 3)} kg`} color="emerald" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">Node TDP vs Memory</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={nodeChartData} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 9 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }} />
              <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
              <Bar dataKey="tdp" name="TDP (W)" fill="#f97316" radius={[4, 4, 0, 0]} />
              <Bar dataKey="mem" name="Memory (GB)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
          <h3 className="text-sm font-semibold text-slate-200 mb-4">Node Cost per Hour</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={nodeChartData} layout="vertical" margin={{ top: 0, right: 30, left: 80, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#94a3b8', fontSize: 9 }} width={80} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
                formatter={(v: any) => [`$${v}/hr`, 'Cost']} />
              <Bar dataKey="cost" name="$/hr" radius={[0, 4, 4, 0]}>
                {nodeChartData.map((_, i) => (
                  <Cell key={i} fill={['#8b5cf6', '#3b82f6', '#10b981', '#f97316', '#ec4899'][i % 5]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
        <h3 className="text-sm font-semibold text-slate-200 mb-4">Hardware Fleet Summary</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-400 text-xs border-b border-slate-700">
                <th className="text-left pb-2 pr-4">Node</th>
                <th className="text-left pb-2 pr-4">Type</th>
                <th className="text-left pb-2 pr-4">Deployment</th>
                <th className="text-right pb-2 pr-4">Count</th>
                <th className="text-right pb-2 pr-4">TDP/unit (W)</th>
                <th className="text-right pb-2 pr-4">Memory (GB)</th>
                <th className="text-right pb-2">$/hr</th>
              </tr>
            </thead>
            <tbody>
              {nodes.map((n: any) => (
                <tr key={n.id} className="border-b border-slate-700/40 hover:bg-slate-700/20">
                  <td className="py-2 pr-4 text-slate-200 font-medium">{n.name}</td>
                  <td className="py-2 pr-4 text-xs">
                    <span className="bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
                      {n.hardware_type?.replace('gpu_nvidia_', 'NVIDIA ').replace('npu_google_tpu', 'TPU').replace('edge_device', 'Edge').toUpperCase()}
                    </span>
                  </td>
                  <td className="py-2 pr-4 text-slate-400 text-xs capitalize">{n.deployment?.replace(/_/g, ' ')}</td>
                  <td className="py-2 pr-4 text-right text-slate-300">{n.count}</td>
                  <td className="py-2 pr-4 text-right text-slate-300">{n.tdp_watts}</td>
                  <td className="py-2 pr-4 text-right text-slate-300">{n.memory_gb}</td>
                  <td className="py-2 text-right text-slate-300">${n.cost_per_hour}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

const TABS = [
  { id: 'overview', label: 'Overview', icon: BarChart2 },
  { id: 'pareto', label: 'Pareto Analysis', icon: TrendingDown },
  { id: 'pipelines', label: 'Pipelines', icon: GitBranch },
  { id: 'carbon', label: 'Carbon Grid', icon: Globe },
  { id: 'telemetry', label: 'Telemetry', icon: Cpu },
]

export default function App() {
  const [tab, setTab] = useState('overview')
  const [lastRefresh, setLastRefresh] = useState(new Date())

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center">
              <Leaf className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white">CarbonSense</span>
            <span className="text-xs text-slate-500 hidden sm:block">AI Energy Observability</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500 hidden md:block">Updated {lastRefresh.toLocaleTimeString()}</span>
            <button onClick={() => setLastRefresh(new Date())}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors">
              <RefreshCw className="w-4 h-4" />
            </button>
            <div className="flex items-center gap-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-3 py-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs text-emerald-400 font-medium">Live</span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-1 mb-6 bg-slate-900/60 border border-slate-800 rounded-xl p-1 overflow-x-auto">
          {TABS.map(t => {
            const Icon = t.icon
            return (
              <button key={t.id} onClick={() => setTab(t.id)}
                className={cn('flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all',
                  tab === t.id
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60')}>
                <Icon className="w-4 h-4" />
                {t.label}
              </button>
            )
          })}
        </div>

        {tab === 'overview' && <OverviewTab />}
        {tab === 'pareto' && <ParetoTab />}
        {tab === 'pipelines' && <PipelinesTab />}
        {tab === 'carbon' && <CarbonGridTab />}
        {tab === 'telemetry' && <TelemetryTab />}
      </div>
    </div>
  )
}
