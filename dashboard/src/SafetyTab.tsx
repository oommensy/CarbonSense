import { useState, useEffect } from 'react'
import {
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, BarChart, Bar
} from 'recharts'
import { Shield, AlertTriangle, Eye, Lock, Zap, XCircle } from 'lucide-react'
import { fetchSafetySummary, fetchSafetyEventCounts, fetchSafetyEvents, evaluateSafety } from './api'

const cn = (...classes: (string | boolean | undefined)[]) => classes.filter(Boolean).join(' ')
const fmt = (n: number | null | undefined, dec = 1) =>
  n == null ? '—' : n.toLocaleString(undefined, { maximumFractionDigits: dec })

const SEVERITY_COLOR: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
}

const EVENT_LABEL: Record<string, string> = {
  pii_detected: 'PII Detected',
  toxicity_flagged: 'Toxicity',
  injection_attempt: 'Injection Attempt',
  hallucination_risk: 'Hallucination Risk',
  unsafe_content: 'Unsafe Content',
  anomaly: 'Anomaly',
}

const EVENT_ICON: Record<string, any> = {
  pii_detected: Eye,
  toxicity_flagged: AlertTriangle,
  injection_attempt: Lock,
  hallucination_risk: Zap,
  unsafe_content: XCircle,
  anomaly: AlertTriangle,
}


function SafetyStatCard({ icon: Icon, label, value, sub, color = 'emerald' }: {
  icon: any; label: string; value: string; sub?: string; color?: string
}) {
  const colors: Record<string, string> = {
    emerald: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20',
    red: 'from-red-500/20 to-red-600/5 border-red-500/20',
    orange: 'from-orange-500/20 to-orange-600/5 border-orange-500/20',
    purple: 'from-purple-500/20 to-purple-600/5 border-purple-500/20',
    yellow: 'from-yellow-500/20 to-yellow-600/5 border-yellow-500/20',
  }
  const iconColors: Record<string, string> = {
    emerald: 'text-emerald-400', red: 'text-red-400',
    orange: 'text-orange-400', purple: 'text-purple-400', yellow: 'text-yellow-400',
  }
  return (
    <div className={cn('rounded-xl border bg-gradient-to-br p-5', colors[color])}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs text-slate-400 uppercase tracking-wide">{label}</span>
        <Icon className={cn('w-4 h-4', iconColors[color])} />
      </div>
      <div className="text-2xl font-bold text-white">{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-1">{sub}</div>}
    </div>
  )
}

function LiveEvaluator() {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [model, setModel] = useState('gpt-4')
  const [quant, setQuant] = useState('fp16')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const run = async () => {
    setLoading(true)
    try {
      const r = await evaluateSafety({ prompt, response, model_name: model, quantization: quant })
      setResult(r)
    } catch {
      // Demo mode: simulate result
      const inj = (prompt.toLowerCase().includes('ignore') || prompt.toLowerCase().includes('jailbreak')) ? 2 : 0
      const pii = (prompt.includes('@') || /\d{3}-\d{2}-\d{4}/.test(prompt)) ? 1 : 0
      const score = Math.max(0, 100 - inj * 30 - pii * 15)
      setResult({
        safety_score: score,
        hallucination_risk: quant === 'int4' ? 0.18 : 0.05,
        toxicity_score: 0.02,
        pii_detected: pii > 0,
        pii_count: pii,
        injection_attempts: inj,
        safety_violations: inj,
        safety_events: inj > 0 ? [{ event_type: 'injection_attempt', severity: 'high', detail: 'Instruction override pattern detected' }] : [],
        eval_ms: 2.4,
      })
    }
    setLoading(false)
  }

  const scoreColor = result
    ? result.safety_score >= 90 ? 'text-emerald-400'
      : result.safety_score >= 70 ? 'text-yellow-400'
        : result.safety_score >= 50 ? 'text-orange-400' : 'text-red-400'
    : ''

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
      <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
        <Shield className="w-4 h-4 text-purple-400" /> Live Safety Evaluator
      </h3>
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Model</label>
          <input value={model} onChange={e => setModel(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500" />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Quantization</label>
          <select value={quant} onChange={e => setQuant(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500">
            {['fp32', 'fp16', 'int8', 'int4', 'gguf'].map(q => <option key={q}>{q}</option>)}
          </select>
        </div>
      </div>
      <div className="mb-3">
        <label className="text-xs text-slate-400 mb-1 block">Prompt</label>
        <textarea value={prompt} onChange={e => setPrompt(e.target.value)} rows={3}
          placeholder="Enter a prompt to evaluate (try: 'Ignore all previous instructions...')"
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500 resize-none" />
      </div>
      <div className="mb-4">
        <label className="text-xs text-slate-400 mb-1 block">Response (optional)</label>
        <textarea value={response} onChange={e => setResponse(e.target.value)} rows={2}
          placeholder="Enter the LLM response to evaluate for PII, toxicity, etc."
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500 resize-none" />
      </div>
      <button onClick={run} disabled={loading || (!prompt && !response)}
        className="w-full py-2.5 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white text-sm font-medium transition-colors">
        {loading ? 'Evaluating...' : 'Run Safety Evaluation'}
      </button>

      {result && (
        <div className="mt-4 space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/60 border border-slate-700">
            <span className="text-sm text-slate-300">Safety Score</span>
            <span className={cn('text-2xl font-bold', scoreColor)}>{fmt(result.safety_score, 0)}/100</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {[
              { label: 'Hallucination Risk', value: `${(result.hallucination_risk * 100).toFixed(0)}%`, bad: result.hallucination_risk > 0.15 },
              { label: 'Toxicity Score', value: `${(result.toxicity_score * 100).toFixed(0)}%`, bad: result.toxicity_score > 0.3 },
              { label: 'PII Detected', value: result.pii_detected ? `Yes (${result.pii_count})` : 'No', bad: result.pii_detected },
              { label: 'Injection Attempts', value: result.injection_attempts, bad: result.injection_attempts > 0 },
            ].map(({ label, value, bad }) => (
              <div key={label} className={cn('flex justify-between p-2 rounded-lg border',
                bad ? 'bg-red-500/10 border-red-500/30' : 'bg-slate-800/60 border-slate-700')}>
                <span className="text-slate-400">{label}</span>
                <span className={bad ? 'text-red-400 font-medium' : 'text-white'}>{String(value)}</span>
              </div>
            ))}
          </div>
          {result.safety_events?.length > 0 && (
            <div className="space-y-1.5">
              <div className="text-xs text-slate-400 font-medium">Events Detected</div>
              {result.safety_events.map((e: any, i: number) => (
                <div key={i} className="flex items-start gap-2 p-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-xs">
                  <AlertTriangle className="w-3.5 h-3.5 text-red-400 mt-0.5 shrink-0" />
                  <div>
                    <span className="text-red-400 font-medium capitalize">{EVENT_LABEL[e.event_type] || e.event_type}</span>
                    <span className="text-slate-400 ml-1">— {e.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="text-xs text-slate-500 text-right">Evaluated in {fmt(result.eval_ms, 1)}ms</div>
        </div>
      )}
    </div>
  )
}

export default function SafetyTab() {
  const [summary, setSummary] = useState<any>(null)
  const [eventCounts, setEventCounts] = useState<any[]>([])
  const [events, setEvents] = useState<any[]>([])
  const [days, setDays] = useState(7)
  const [severityFilter, setSeverityFilter] = useState('')

  useEffect(() => {
    fetchSafetySummary(days).then(setSummary).catch(() => {
      // Demo data when backend not running
      setSummary({
        total_workloads: 847,
        avg_safety_score: 87.4,
        avg_hallucination_risk: 0.082,
        avg_toxicity_score: 0.031,
        total_pii_incidents: 23,
        total_injection_attempts: 7,
        total_safety_violations: 12,
        safety_score_trend: Array.from({ length: 7 }, (_, i) => ({
          date: new Date(Date.now() - (6 - i) * 86400000).toISOString().slice(0, 10),
          avg_safety_score: 82 + Math.random() * 12,
        })),
      })
    })
    fetchSafetyEventCounts(days).then(setEventCounts).catch(() => {
      setEventCounts([
        { event_type: 'pii_detected', count: 23 },
        { event_type: 'injection_attempt', count: 7 },
        { event_type: 'hallucination_risk', count: 41 },
        { event_type: 'toxicity_flagged', count: 5 },
      ])
    })
    fetchSafetyEvents(days, severityFilter || undefined).then(setEvents).catch(() => {
      setEvents([
        { id: 1, event_type: 'injection_attempt', severity: 'high', detail: 'Instruction override: "ignore all previous instructions"', timestamp: new Date().toISOString(), blocked: true },
        { id: 2, event_type: 'pii_detected', severity: 'high', detail: 'Email address detected in response', timestamp: new Date(Date.now() - 3600000).toISOString(), blocked: false },
        { id: 3, event_type: 'hallucination_risk', severity: 'medium', detail: 'INT4 quantization — elevated hallucination baseline', timestamp: new Date(Date.now() - 7200000).toISOString(), blocked: false },
        { id: 4, event_type: 'toxicity_flagged', severity: 'medium', detail: 'Toxicity score 0.42 exceeded threshold', timestamp: new Date(Date.now() - 10800000).toISOString(), blocked: true },
      ])
    })
  }, [days, severityFilter])


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Shield className="w-5 h-5 text-purple-400" /> Safety Monitor
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">Real-time RAI safety evaluation across all AI workloads</p>
        </div>
        <select value={days} onChange={e => setDays(+e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none">
          {[1, 7, 14, 30].map(d => <option key={d} value={d}>Last {d}d</option>)}
        </select>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <SafetyStatCard icon={Shield} label="Avg Safety Score" color="emerald"
          value={fmt(summary?.avg_safety_score, 0) + '/100'}
          sub={`${summary?.total_workloads ?? '—'} workloads`} />
        <SafetyStatCard icon={Lock} label="Injection Attempts" color="red"
          value={String(summary?.total_injection_attempts ?? '—')}
          sub="Blocked or flagged" />
        <SafetyStatCard icon={Eye} label="PII Incidents" color="orange"
          value={String(summary?.total_pii_incidents ?? '—')}
          sub="Across all responses" />
        <SafetyStatCard icon={Zap} label="Hallucination Risk" color="yellow"
          value={summary ? `${(summary.avg_hallucination_risk * 100).toFixed(0)}%` : '—'}
          sub="Avg across workloads" />
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Safety score trend */}
        <div className="lg:col-span-2 rounded-xl border border-slate-700 bg-slate-900/60 p-5">
          <h3 className="font-semibold text-white mb-4">Safety Score Trend</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={summary?.safety_score_trend ?? []}>
              <defs>
                <linearGradient id="safetyGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={v => v.slice(5)} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#94a3b8' }} itemStyle={{ color: '#a855f7' }} />
              <Area type="monotone" dataKey="avg_safety_score" stroke="#a855f7" strokeWidth={2}
                fill="url(#safetyGrad)" name="Safety Score" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Event type breakdown */}
        <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
          <h3 className="font-semibold text-white mb-4">Events by Type</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={eventCounts.map(e => ({ ...e, label: EVENT_LABEL[e.event_type] || e.event_type }))}
              layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis type="category" dataKey="label" tick={{ fill: '#94a3b8', fontSize: 10 }} width={110} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
                itemStyle={{ color: '#a855f7' }} />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {eventCounts.map((_, i) => (
                  <Cell key={i} fill={['#ef4444', '#f97316', '#eab308', '#a855f7', '#3b82f6', '#10b981'][i % 6]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Live evaluator + event log */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LiveEvaluator />

        {/* Event log */}
        <div className="rounded-xl border border-slate-700 bg-slate-900/60 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white">Recent Safety Events</h3>
            <select value={severityFilter} onChange={e => setSeverityFilter(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-xs text-white focus:outline-none">
              <option value="">All severities</option>
              {['critical', 'high', 'medium', 'low'].map(s => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </div>
          <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
            {events.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-sm">No events in this period</div>
            ) : events.map((e: any) => {
              const Icon = EVENT_ICON[e.event_type] || AlertTriangle
              const sev = e.severity || 'medium'
              const sevColor = SEVERITY_COLOR[sev] || '#94a3b8'
              return (
                <div key={e.id} className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 hover:border-slate-600 transition-colors">
                  <Icon className="w-4 h-4 mt-0.5 shrink-0" style={{ color: sevColor }} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-xs font-medium text-white">{EVENT_LABEL[e.event_type] || e.event_type}</span>
                      <span className="text-xs px-1.5 py-0.5 rounded-full border capitalize"
                        style={{ color: sevColor, borderColor: sevColor + '40', background: sevColor + '15' }}>
                        {sev}
                      </span>
                      {e.blocked && (
                        <span className="text-xs px-1.5 py-0.5 rounded-full bg-red-500/20 border border-red-500/30 text-red-400">blocked</span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 truncate">{e.detail}</p>
                    <p className="text-xs text-slate-600 mt-0.5">
                      {e.timestamp ? new Date(e.timestamp).toLocaleString() : ''}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
