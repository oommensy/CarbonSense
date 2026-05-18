import { useState, useEffect } from 'react'
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell
} from 'recharts'
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Minus, Info } from 'lucide-react'
import { fetchGlobalInsights, fetchScatterData, fetchCorrelations } from './api'

const cn = (...classes: (string | boolean | undefined)[]) => classes.filter(Boolean).join(' ')
const fmt = (n: number | null | undefined, dec = 1) =>
  n == null ? '—' : n.toLocaleString(undefined, { maximumFractionDigits: dec })

const QUANT_COLORS: Record<string, string> = {
  fp32: '#6366f1', fp16: '#3b82f6', int8: '#10b981', int4: '#f59e0b', gguf: '#ef4444',
}

const SCATTER_METRICS = [
  { value: 'total_carbon_g_co2e', label: 'Carbon (g CO2e)' },
  { value: 'safety_score', label: 'Safety Score' },
  { value: 'avg_latency_ms', label: 'Latency (ms)' },
  { value: 'total_energy_kwh', label: 'Energy (kWh)' },
  { value: 'hallucination_risk', label: 'Hallucination Risk' },
  { value: 'compute_cost_usd', label: 'Cost (USD)' },
  { value: 'green_score', label: 'Green Score' },
]

function InsightCard({ insight }: { insight: any }) {
  // isPositive unused
  const isWarning = insight.severity === 'warning'
  const isCritical = insight.severity === 'critical'

  const borderColor = isCritical ? 'border-red-500/40' : isWarning ? 'border-yellow-500/40' : 'border-emerald-500/40'
  const bgColor = isCritical ? 'bg-red-500/5' : isWarning ? 'bg-yellow-500/5' : 'bg-emerald-500/5'
  const Icon = isCritical ? AlertTriangle : isWarning ? AlertTriangle : CheckCircle
  const iconColor = isCritical ? 'text-red-400' : isWarning ? 'text-yellow-400' : 'text-emerald-400'

  const DeltaChip = ({ label, value, unit = '%', invertGood = false }: {
    label: string; value: number; unit?: string; invertGood?: boolean
  }) => {
    const isGood = invertGood ? value < 0 : value > 0
    const isNeutral = Math.abs(value) < 0.5
    const color = isNeutral ? 'text-slate-400' : isGood ? 'text-emerald-400' : 'text-red-400'
    const Arrow = isNeutral ? Minus : value > 0 ? TrendingUp : TrendingDown
    return (
      <div className="flex flex-col items-center p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/60 min-w-[80px]">
        <span className="text-xs text-slate-500 mb-1">{label}</span>
        <div className={cn('flex items-center gap-1 font-semibold text-sm', color)}>
          <Arrow className="w-3.5 h-3.5" />
          {value > 0 ? '+' : ''}{fmt(value, 0)}{unit}
        </div>
      </div>
    )
  }

  return (
    <div className={cn('rounded-xl border p-5', borderColor, bgColor)}>
      <div className="flex items-start gap-3 mb-3">
        <Icon className={cn('w-5 h-5 mt-0.5 shrink-0', iconColor)} />
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-white text-sm">{insight.title}</h3>
            <span className={cn('text-xs px-2 py-0.5 rounded-full border capitalize',
              isCritical ? 'bg-red-500/20 border-red-500/30 text-red-400'
                : isWarning ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400'
                  : 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400')}>
              {insight.severity}
            </span>
            <span className="text-xs text-slate-500">n={insight.sample_size} · {(insight.confidence * 100).toFixed(0)}% confidence</span>
          </div>
          <p className="text-xs text-slate-400 mt-1">{insight.description}</p>
        </div>
      </div>

      {/* Delta chips */}
      <div className="flex gap-2 flex-wrap mb-3">
        <DeltaChip label="Carbon" value={insight.carbon_change_pct} invertGood />
        <DeltaChip label="Latency" value={insight.latency_change_pct} invertGood />
        <DeltaChip label="Safety" value={insight.safety_change_pts} unit="pts" />
        <DeltaChip label="Halluc. Risk" value={insight.hallucination_change_pct} invertGood />
        <DeltaChip label="Cost" value={insight.cost_change_pct} invertGood />
      </div>

      {/* Recommendation */}
      <div className="flex items-start gap-2 p-3 rounded-lg bg-slate-900/60 border border-slate-700/40">
        <Info className="w-3.5 h-3.5 text-blue-400 mt-0.5 shrink-0" />
        <p className="text-xs text-slate-300">{insight.recommendation}</p>
      </div>
    </div>
  )
}

function CorrelationHeatmap({ pairs }: { pairs: any[] }) {
  if (!pairs?.length) return null
  const top = pairs.slice(0, 8)
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
      <h3 className="font-semibold text-white mb-4">Metric Correlations</h3>
      <div className="space-y-2">
        {top.map((p: any, corrIdx: number) => {
          const r = p.correlation
          const abs = Math.abs(r)
          const color = r > 0 ? '#3b82f6' : '#ef4444'
          const label = `${p.x.replace(/_/g, ' ')} ↔ ${p.y.replace(/_/g, ' ')}`
          return (
            <div key={corrIdx} className="flex items-center gap-3">
              <div className="text-xs text-slate-400 w-64 truncate">{label}</div>
              <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all"
                  style={{ width: `${abs * 100}%`, background: color }} />
              </div>
              <div className="text-xs font-mono w-12 text-right" style={{ color }}>
                {r > 0 ? '+' : ''}{r.toFixed(2)}
              </div>
              <div className="text-xs text-slate-500 w-14 capitalize">{p.strength}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function TradeoffTab() {
  const [insights, setInsights] = useState<any[]>([])
  const [correlations, setCorrelations] = useState<any[]>([])
  const [scatter, setScatter] = useState<any[]>([])
  const [xMetric, setXMetric] = useState('total_carbon_g_co2e')
  const [yMetric, setYMetric] = useState('safety_score')
  const [days, setDays] = useState(7)
  const [summary, setSummary] = useState('')

  useEffect(() => {
    fetchGlobalInsights(days).then((d: any) => {
      setInsights(d.insights || [])
      setSummary(d.summary || '')
    }).catch(() => {
      // Demo insights
      setInsights([
        {
          title: 'Quantization: FP16 → INT8',
          description: 'Switching from FP16 to INT8 reduced carbon by 31% and improved latency by 18%, but safety score dropped by 6.2 points and hallucination risk increased 14%.',
          optimization: 'quantization:fp16→int8',
          carbon_change_pct: -31.2,
          energy_change_pct: -29.8,
          latency_change_pct: -18.4,
          safety_change_pts: -6.2,
          hallucination_change_pct: 14.1,
          toxicity_change_pct: 2.3,
          cost_change_pct: -28.5,
          confidence: 0.87,
          severity: 'warning',
          recommendation: 'INT8 offers strong efficiency gains. Run a 7-day safety eval before full production rollout. Consider a hybrid approach: INT8 for low-risk workloads, FP16 for sensitive pipelines.',
          sample_size: 234,
        },
        {
          title: 'Quantization: INT8 → INT4',
          description: 'INT4 reduced carbon by a further 22% but caused a critical 14-point safety score drop and hallucination risk increased 28%. Not recommended for production.',
          optimization: 'quantization:int8→int4',
          carbon_change_pct: -22.1,
          energy_change_pct: -21.3,
          latency_change_pct: -9.2,
          safety_change_pts: -14.3,
          hallucination_change_pct: 28.4,
          toxicity_change_pct: 5.1,
          cost_change_pct: -19.8,
          confidence: 0.91,
          severity: 'critical',
          recommendation: 'INT4 quantization causes significant safety regression. Avoid for customer-facing LLM workloads. Only use for internal batch processing with human review.',
          sample_size: 187,
        },
        {
          title: 'Deployment: Cloud → Edge',
          description: 'Edge inference reduced carbon by 43% vs cloud with no statistically significant safety regression. Latency improved 22% for regional users.',
          optimization: 'deployment:cloud→edge',
          carbon_change_pct: -43.2,
          energy_change_pct: -41.7,
          latency_change_pct: -22.1,
          safety_change_pts: -1.8,
          hallucination_change_pct: 3.2,
          toxicity_change_pct: 0.4,
          cost_change_pct: -38.9,
          confidence: 0.79,
          severity: 'positive',
          recommendation: 'Edge deployment is strongly recommended for this pipeline. 43% carbon reduction with negligible safety impact. Prioritise EU-North and US-West regions for lowest grid intensity.',
          sample_size: 156,
        },
      ])
      setSummary('Analysed 847 workloads, found 3 trade-off insights. ⚠ 1 critical trade-off requires attention: INT8 → INT4 causes safety regression. ✓ 1 optimization opportunity: Cloud → Edge deployment.')
    })

    fetchCorrelations(days).then((d: any) => setCorrelations(d.pairs || [])).catch(() => {
      setCorrelations([
        { x: 'total_carbon_g_co2e', y: 'avg_latency_ms', correlation: 0.84, strength: 'strong', direction: 'positive' },
        { x: 'safety_score', y: 'hallucination_risk', correlation: -0.76, strength: 'strong', direction: 'negative' },
        { x: 'total_energy_kwh', y: 'compute_cost_usd', correlation: 0.91, strength: 'strong', direction: 'positive' },
        { x: 'total_carbon_g_co2e', y: 'safety_score', correlation: -0.42, strength: 'moderate', direction: 'negative' },
        { x: 'avg_latency_ms', y: 'safety_score', correlation: -0.38, strength: 'weak', direction: 'negative' },
        { x: 'total_energy_kwh', y: 'hallucination_risk', correlation: 0.29, strength: 'weak', direction: 'positive' },
      ])
    })
  }, [days])

  useEffect(() => {
    fetchScatterData(xMetric, yMetric, days).then((d: any) => setScatter(d.points || [])).catch(() => {
      // Demo scatter
      const quantizations = ['fp32', 'fp16', 'int8', 'int4']
      const pts = Array.from({ length: 60 }, (_) => {
        const q = quantizations[Math.floor(Math.random() * quantizations.length)]
        const qFactor = q === 'fp32' ? 1.0 : q === 'fp16' ? 0.75 : q === 'int8' ? 0.55 : 0.38
        return {
          x: +(Math.random() * 0.8 * qFactor + 0.05).toFixed(4),
          y: +(85 + (Math.random() - 0.5) * 20 - (1 - qFactor) * 15).toFixed(1),
          quantization: q,
          model: ['llama-3-70b', 'gpt-4', 'mistral-7b', 'llama-3-8b'][Math.floor(Math.random() * 4)],
        }
      })
      setScatter(pts)
    })
  }, [xMetric, yMetric, days])

  const xLabel = SCATTER_METRICS.find(m => m.value === xMetric)?.label || xMetric
  const yLabel = SCATTER_METRICS.find(m => m.value === yMetric)?.label || yMetric

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-400" /> Trade-off Intelligence
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            How every optimization decision affects safety, carbon, and performance — simultaneously
          </p>
        </div>
        <select value={days} onChange={e => setDays(+e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none">
          {[7, 14, 30, 90].map(d => <option key={d} value={d}>Last {d}d</option>)}
        </select>
      </div>

      {/* Summary banner */}
      {summary && (
        <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-4 flex items-start gap-3">
          <Info className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
          <p className="text-sm text-slate-300">{summary}</p>
        </div>
      )}

      {/* Scatter plot */}
      <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
          <h3 className="font-semibold text-white">Metric Scatter Plot</h3>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">X:</span>
              <select value={xMetric} onChange={e => setXMetric(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-xs text-white focus:outline-none">
                {SCATTER_METRICS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Y:</span>
              <select value={yMetric} onChange={e => setYMetric(e.target.value)}
                className="bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-xs text-white focus:outline-none">
                {SCATTER_METRICS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Quantization legend */}
        <div className="flex gap-4 mb-3 flex-wrap">
          {Object.entries(QUANT_COLORS).map(([q, color]) => (
            <div key={q} className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />
              <span className="text-xs text-slate-400 uppercase">{q}</span>
            </div>
          ))}
        </div>

        <ResponsiveContainer width="100%" height={280}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="x" name={xLabel} tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: xLabel, position: 'insideBottom', offset: -5, fill: '#64748b', fontSize: 11 }} />
            <YAxis dataKey="y" name={yLabel} tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: yLabel, angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
              labelStyle={{ color: '#94a3b8' }}
              formatter={(value: any) => [fmt(+value, 3)]}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null
                const d = payload[0]?.payload
                return (
                  <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs">
                    <div className="font-medium text-white mb-1">{d?.model}</div>
                    <div className="text-slate-400">Quantization: <span className="text-white uppercase">{d?.quantization}</span></div>
                    <div className="text-slate-400">{xLabel}: <span className="text-white">{fmt(d?.x, 4)}</span></div>
                    <div className="text-slate-400">{yLabel}: <span className="text-white">{fmt(d?.y, 2)}</span></div>
                  </div>
                )
              }}
            />
            <Scatter data={scatter} name="Workloads">
              {scatter.map((pt: any, ptIdx: number) => (
                <Cell key={ptIdx} fill={QUANT_COLORS[pt.quantization] || '#94a3b8'} fillOpacity={0.75} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
        <p className="text-xs text-slate-500 mt-2 text-center">
          Each point = one workload. Color = quantization level. {scatter.length} workloads plotted.
        </p>
      </div>

      {/* Insights */}
      <div>
        <h3 className="font-semibold text-white mb-3">Optimization Trade-off Insights</h3>
        {insights.length === 0 ? (
          <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-8 text-center text-slate-500 text-sm">
            Not enough data yet. Run workloads with different quantization or deployment settings to generate insights.
          </div>
        ) : (
          <div className="space-y-4">
            {insights.map((insight: any, i: number) => (
              <InsightCard key={i} insight={insight} />
            ))}
          </div>
        )}
      </div>

      {/* Correlation matrix */}
      <CorrelationHeatmap pairs={correlations} />

      {/* SDK callout */}
      <div className="rounded-xl border border-blue-500/30 bg-blue-500/5 p-5">
        <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-blue-400" /> Generate Your Own Insights
        </h3>
        <p className="text-sm text-slate-400 mb-3">
          Instrument your LLM calls with the CarbonSense SDK to start generating real trade-off data.
        </p>
        <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-xs text-emerald-400 overflow-x-auto">{`pip install carbonsense

from carbonsense import monitor

# One line — tracks performance, energy, carbon, and safety
monitor.track_llm(
    provider="openai", model="gpt-4",
    prompt=prompt, response=response,
    latency_ms=120, token_usage=350,
    quantization="int8",
)

# Or wrap your OpenAI client automatically
client = monitor.wrap_openai(openai.OpenAI())`}</pre>
      </div>
    </div>
  )
}
