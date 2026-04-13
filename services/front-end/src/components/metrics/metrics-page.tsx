import { useState } from 'react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useMetricsPage } from '@/hooks/use-metrics-page'
import type { AgentSessionDetail, AgentSessionListItem, MetricsJob, TokensReport } from '@/lib/metrics-api'

function JobStatusBadge({ job, label }: { job: MetricsJob | null; label: string }) {
  if (!job) return <span className="text-xs text-[#667781]">{label}: nunca executado</span>

  const statusColor =
    job.status === 'done'
      ? 'text-[#00a884] bg-[#d9fdd3]'
      : job.status === 'running'
        ? 'text-amber-600 bg-amber-50'
        : 'text-red-500 bg-red-50'

  const statusLabel =
    job.status === 'done' ? 'Concluído' : job.status === 'running' ? 'Em andamento' : 'Erro'

  const ts = job.finished_at ?? job.started_at
  const date = new Date(ts).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-[#667781]">{label}:</span>
      <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${statusColor}`}>
        {statusLabel}
      </span>
      <span className="text-xs text-[#667781]">{date}</span>
      {job.error_message && (
        <span className="text-xs text-red-400" title={job.error_message}>⚠ {job.error_message.slice(0, 40)}</span>
      )}
    </div>
  )
}

function IndexCard({ value, label }: { value: number; label: string }) {
  const color =
    value > 30 ? 'text-[#00a884]' : value < 0 ? 'text-red-500' : 'text-amber-500'
  const bg =
    value > 30 ? 'bg-[#d9fdd3]' : value < 0 ? 'bg-red-50' : 'bg-amber-50'
  const sign = value > 0 ? '+' : ''

  return (
    <div className={`flex flex-col items-center justify-center rounded-2xl p-6 ${bg}`}>
      <span className={`text-5xl font-bold tabular-nums ${color}`}>
        {sign}{value}
      </span>
      <span className="mt-2 text-center text-sm font-medium text-[#667781]">{label}</span>
    </div>
  )
}

function SatisfactionBar({
  label,
  pct,
  count,
  color,
}: {
  label: string
  pct: number
  count: number
  color: string
}) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-14 text-right text-sm font-semibold text-[#111b21]">{label}</span>
      <div className="flex-1 overflow-hidden rounded-full bg-[#e9edef]" style={{ height: 12 }}>
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${Math.max(pct, 0)}%` }}
        />
      </div>
      <span className="w-24 text-sm text-[#667781]">
        {pct}% <span className="text-xs">({count})</span>
      </span>
    </div>
  )
}

function ScoreGauge({
  label,
  value,
  max,
  description,
}: {
  label: string
  value: number
  max: number
  description: string
}) {
  const pct = max > 0 ? (value / max) * 100 : 0
  const color = pct >= 66 ? 'bg-[#00a884]' : pct >= 33 ? 'bg-amber-400' : 'bg-red-400'

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between">
        <span className="text-sm font-semibold text-[#111b21]">{label}</span>
        <span className="text-xl font-bold tabular-nums text-[#111b21]">
          {value.toFixed(1)}<span className="text-sm font-normal text-[#667781]">/{max}</span>
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-[#e9edef]">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-[#667781]">{description}</span>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col gap-1 rounded-2xl border border-black/6 bg-white p-5">
      <span className="text-2xl font-bold tabular-nums text-[#111b21]">{value}</span>
      <span className="text-xs font-medium uppercase tracking-wider text-[#667781]">{label}</span>
    </div>
  )
}

// ─── Satisfaction badge ───────────────────────────────────────────────────────
function SatisfactionBadge({ value }: { value: string }) {
  const styles: Record<string, string> = {
    bom: 'bg-[#d9fdd3] text-[#00a884]',
    neutro: 'bg-amber-50 text-amber-600',
    ruim: 'bg-red-50 text-red-500',
  }
  const labels: Record<string, string> = { bom: '😊 Bom', neutro: '😐 Neutro', ruim: '😞 Ruim' }
  const cls = styles[value] ?? 'bg-[#e9edef] text-[#667781]'
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {labels[value] ?? value}
    </span>
  )
}

// ─── Session detail modal ─────────────────────────────────────────────────────
function SessionDetailModal({
  detail,
  onClose,
}: {
  detail: AgentSessionDetail
  onClose: () => void
}) {
  const [promptOpen, setPromptOpen] = useState(false)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="relative flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b border-black/6 p-5">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <SatisfactionBadge value={detail.satisfaction} />
              {detail.prompt_injection_detected && (
                <span className="rounded-full bg-red-50 px-2 py-0.5 text-xs font-semibold text-red-500">
                  🔴 Injeção detectada
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-[#111b21]">{detail.objetivo_cliente || '—'}</p>
            <p className="text-xs text-[#667781]">
              ID: {detail.session_id.slice(0, 8)}…
            </p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 shrink-0 rounded-full p-1.5 text-[#667781] hover:bg-[#e9edef]"
          >
            ✕
          </button>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* Scores */}
          <section>
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-[#667781]">
              Scores
            </h3>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                { label: 'Satisfação', raw: detail.satisfaction },
                { label: 'Esforço', value: `${detail.effort_score}/5` },
                { label: 'Entendimento', value: `${detail.understanding_score}/2` },
                { label: 'Resolução', value: `${detail.resolution_score}/2` },
              ].map((s) => (
                <div key={s.label} className="rounded-xl border border-black/6 p-3 text-center">
                  <p className="text-xs text-[#667781]">{s.label}</p>
                  <p className="mt-1 text-lg font-bold text-[#111b21]">
                    {s.value ?? <SatisfactionBadge value={s.raw ?? ''} />}
                  </p>
                </div>
              ))}
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3">
              {detail.mudanca_comportamental && (
                <div className="rounded-xl border border-black/6 p-3">
                  <p className="text-xs text-[#667781]">Mudança comportamental</p>
                  <p className="mt-1 text-sm font-semibold text-[#111b21] capitalize">
                    {detail.mudanca_comportamental}
                  </p>
                </div>
              )}
              {detail.sinal_fechamento && (
                <div className="rounded-xl border border-black/6 p-3">
                  <p className="text-xs text-[#667781]">Sinal de fechamento</p>
                  <p className="mt-1 text-sm font-semibold text-[#111b21] capitalize">
                    {detail.sinal_fechamento}
                  </p>
                </div>
              )}
            </div>
            {detail.total_tokens != null && (
              <p className="mt-2 text-xs text-[#667781]">
                Tokens usados: {detail.total_tokens.toLocaleString()} (prompt: {detail.prompt_tokens?.toLocaleString() ?? '—'} · resposta: {detail.completion_tokens?.toLocaleString() ?? '—'})
              </p>
            )}
          </section>

          {/* Evidences */}
          {detail.evidences.length > 0 && (
            <section>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-[#667781]">
                Evidências
              </h3>
              <ul className="space-y-1">
                {detail.evidences.map((ev, i) => (
                  <li key={i} className="rounded-lg bg-[#f0f2f5] px-3 py-2 text-sm text-[#111b21]">
                    "{ev}"
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Injection snippets */}
          {detail.injection_snippets.length > 0 && (
            <section>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-red-400">
                Trechos de injeção
              </h3>
              <ul className="space-y-1">
                {detail.injection_snippets.map((s, i) => (
                  <li key={i} className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
                    "{s}"
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Conversation */}
          <section>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-[#667781]">
              Conversa analisada ({detail.messages.length} mensagens)
            </h3>
            <div className="space-y-2">
              {detail.messages.map((msg, i) => {
                const isUser = msg.role === 'user'
                return (
                  <div
                    key={i}
                    className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-xl px-3 py-2 text-sm ${
                        isUser
                          ? 'bg-[#d9fdd3] text-[#111b21]'
                          : 'bg-[#f0f2f5] text-[#111b21]'
                      }`}
                    >
                      <p className="mb-0.5 text-[10px] font-semibold uppercase text-[#667781]">
                        {isUser ? 'Usuário' : 'IA'}
                      </p>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </section>

          {/* Prompt used — collapsible */}
          <section>
            <button
              onClick={() => setPromptOpen((p) => !p)}
              className="flex w-full items-center justify-between rounded-xl border border-black/6 px-4 py-3 text-sm font-semibold text-[#111b21] hover:bg-[#f0f2f5]"
            >
              <span>Prompt utilizado pelo agente</span>
              <span>{promptOpen ? '▲' : '▼'}</span>
            </button>
            {promptOpen && (
              <pre className="mt-2 overflow-x-auto rounded-xl bg-[#f0f2f5] p-4 text-xs text-[#111b21] whitespace-pre-wrap">
                {detail.prompt_used}
              </pre>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}

// ─── Session card ─────────────────────────────────────────────────────────────
function SessionCard({
  session,
  onClick,
}: {
  session: AgentSessionListItem
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col gap-3 rounded-2xl border border-black/6 bg-white p-5 text-left transition hover:shadow-md hover:border-[#00a884]/40"
    >
      <div className="flex items-start justify-between gap-2">
        <SatisfactionBadge value={session.satisfaction} />
        <div className="flex items-center gap-1.5">
          {session.prompt_injection_detected && (
            <span title="Injeção detectada" className="text-sm">🔴</span>
          )}
          {session.total_tokens != null && (
            <span className="text-xs text-[#667781]">{session.total_tokens.toLocaleString()} tk</span>
          )}
        </div>
      </div>

      <p className="line-clamp-2 text-sm text-[#111b21]">
        {session.objetivo_cliente || <span className="italic text-[#667781]">Objetivo não identificado</span>}
      </p>

      <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-[#667781]">
        <span>Esforço {session.effort_score}/5</span>
        <span>Entend. {session.understanding_score}/2</span>
        <span>Resol. {session.resolution_score}/2</span>
        {session.mudanca_comportamental && <span className="capitalize">{session.mudanca_comportamental}</span>}
      </div>

      <p className="text-[10px] text-[#adb5bd]">{session.session_id.slice(0, 16)}…</p>
    </button>
  )
}

// ─── Resultados Unitários tab ─────────────────────────────────────────────────
function ResultadosUnitariosTab({
  sessions,
  loadDetail,
}: {
  sessions: AgentSessionListItem[]
  loadDetail: (id: string) => Promise<AgentSessionDetail>
}) {
  const [selectedDetail, setSelectedDetail] = useState<AgentSessionDetail | null>(null)
  const [loadingId, setLoadingId] = useState<string | null>(null)

  async function openDetail(sessionId: string) {
    setLoadingId(sessionId)
    try {
      const detail = await loadDetail(sessionId)
      setSelectedDetail(detail)
    } finally {
      setLoadingId(null)
    }
  }

  if (sessions.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center py-20">
        <p className="text-sm text-[#667781]">Nenhuma análise disponível. Execute "Analisar" primeiro.</p>
      </div>
    )
  }

  return (
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sessions.map((session) => (
          <div key={session.session_id} className="relative">
            {loadingId === session.session_id && (
              <div className="absolute inset-0 z-10 flex items-center justify-center rounded-2xl bg-white/80">
                <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-[#00a884] border-t-transparent" />
              </div>
            )}
            <SessionCard
              session={session}
              onClick={() => void openDetail(session.session_id)}
            />
          </div>
        ))}
      </div>

      {selectedDetail && (
        <SessionDetailModal
          detail={selectedDetail}
          onClose={() => setSelectedDetail(null)}
        />
      )}
    </>
  )
}

// ─── Token charts ─────────────────────────────────────────────────────────────
function TokensTimeSeriesChart({ report }: { report: TokensReport }) {
  if (report.time_series.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center">
        <p className="text-sm text-[#667781]">Sem dados ainda.</p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={report.time_series} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="tokenGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#00a884" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#00a884" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e9edef" />
        <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#667781' }} />
        <YAxis tick={{ fontSize: 11, fill: '#667781' }} width={50} />
        <Tooltip
          contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e9edef' }}
          formatter={(v) => [(v as number).toLocaleString(), 'Tokens']}
        />
        <Area
          type="monotone"
          dataKey="tokens"
          stroke="#00a884"
          strokeWidth={2}
          fill="url(#tokenGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

const MODEL_COLORS = ['#00a884', '#25d366', '#128c7e', '#075e54', '#34b7f1', '#a29bfe']

function TokensByModelChart({ report }: { report: TokensReport }) {
  if (report.by_model.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center">
        <p className="text-sm text-[#667781]">Sem dados ainda.</p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(160, report.by_model.length * 48)}>
      <BarChart
        data={report.by_model}
        layout="vertical"
        margin={{ top: 4, right: 16, left: 8, bottom: 0 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#e9edef" horizontal={false} />
        <XAxis type="number" tick={{ fontSize: 11, fill: '#667781' }} />
        <YAxis type="category" dataKey="model_id" tick={{ fontSize: 11, fill: '#667781' }} width={130} />
        <Tooltip
          contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e9edef' }}
          formatter={(v) => [(v as number).toLocaleString(), 'Tokens']}
        />
        <Bar dataKey="tokens" radius={[0, 4, 4, 0]}>
          {report.by_model.map((_, i) => (
            <Cell key={i} fill={MODEL_COLORS[i % MODEL_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

// ─── Main MetricsPage ─────────────────────────────────────────────────────────
export function MetricsPage({ apiKey }: { apiKey: string }) {
  const {
    metricsSummary,
    evaluationsSummary,
    exportJob,
    analysisJob,
    agentSessions,
    tokensReport,
    isLoading,
    isSyncing,
    isAnalyzing,
    error,
    syncConversations,
    runAnalysis,
    loadAgentSessionDetail,
  } = useMetricsPage(apiKey)

  const [activeTab, setActiveTab] = useState<'gerais' | 'unitarios'>('gerais')

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <span className="text-sm text-[#667781]">Carregando métricas…</span>
      </div>
    )
  }

  const ev = evaluationsSummary
  const op = metricsSummary

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Tab bar */}
      <div className="flex shrink-0 border-b border-black/6 bg-white px-6">
        {([
          { id: 'gerais', label: 'Resultados Gerais' },
          { id: 'unitarios', label: `Resultados Unitários${agentSessions.length > 0 ? ` (${agentSessions.length})` : ''}` },
        ] as const).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`border-b-2 px-4 py-3 text-sm font-semibold transition ${
              activeTab === tab.id
                ? 'border-[#00a884] text-[#00a884]'
                : 'border-transparent text-[#667781] hover:text-[#111b21]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'gerais' ? (
          <div className="mx-auto flex max-w-4xl flex-col gap-6">

            {/* Header */}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h1 className="text-xl font-bold text-[#111b21]">Métricas da IA Operadora</h1>
                <p className="mt-1 text-sm text-[#667781]">Avaliação de qualidade percebida pelo cliente</p>
              </div>

              {/* Action bar */}
              <div className="flex shrink-0 flex-col items-end gap-2">
                <div className="flex gap-2">
                  <button
                    onClick={() => void syncConversations()}
                    disabled={isSyncing || isAnalyzing}
                    className="flex items-center gap-1.5 rounded-xl bg-[#e9edef] px-4 py-2 text-sm font-semibold text-[#111b21] transition hover:bg-[#d1d7db] disabled:opacity-50"
                  >
                    {isSyncing ? (
                      <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    ) : (
                      <span>↑</span>
                    )}
                    Sincronizar
                  </button>
                  <button
                    onClick={() => void runAnalysis()}
                    disabled={isSyncing || isAnalyzing}
                    className="flex items-center gap-1.5 rounded-xl bg-[#00a884] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#008f6f] disabled:opacity-50"
                  >
                    {isAnalyzing ? (
                      <span className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    ) : (
                      <span>▶</span>
                    )}
                    Analisar
                  </button>
                </div>
              </div>
            </div>

            {/* Error banner */}
            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                {error}
              </div>
            )}

            {/* Job status strip */}
            <div className="flex flex-wrap gap-x-6 gap-y-1 rounded-xl border border-black/6 bg-white px-4 py-3">
              <JobStatusBadge job={exportJob} label="Último sync" />
              <JobStatusBadge job={analysisJob} label="Última análise" />
            </div>

            {/* INDICE_IA_OPERADORA */}
            {ev && (
              <section className="rounded-2xl border border-black/6 bg-white p-6">
                <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-[#667781]">
                  Índice IA Operadora
                </h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <IndexCard
                    value={ev.indice_ia_operadora}
                    label="Índice IA Operadora (% bom − % ruim)"
                  />
                  <div className="flex flex-col justify-center gap-1 rounded-2xl border border-black/6 p-5">
                    <span className="text-xs font-medium uppercase tracking-wider text-[#667781]">
                      Sessões avaliadas
                    </span>
                    <span className="text-4xl font-bold tabular-nums text-[#111b21]">{ev.total_evaluated}</span>
                    <span className="text-xs text-[#667781]">avaliações agentica</span>
                  </div>
                  <div className="flex flex-col justify-center gap-2 rounded-2xl border border-black/6 p-5">
                    <span className="text-xs font-medium uppercase tracking-wider text-[#667781]">Interpretação</span>
                    <span className={`text-sm font-semibold ${
                      ev.indice_ia_operadora > 30
                        ? 'text-[#00a884]'
                        : ev.indice_ia_operadora < 0
                        ? 'text-red-500'
                        : 'text-amber-500'
                    }`}>
                      {ev.indice_ia_operadora > 30
                        ? '✓ Boa experiência'
                        : ev.indice_ia_operadora < 0
                        ? '✗ Experiência ruim'
                        : '~ Experiência neutra'}
                    </span>
                    <span className="text-xs text-[#667781]">
                      Negativo = ruim · 0–30 = neutro · &gt;30 = bom
                    </span>
                  </div>
                </div>
              </section>
            )}

            {/* Satisfaction distribution */}
            {ev && (
              <section className="rounded-2xl border border-black/6 bg-white p-6">
                <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-[#667781]">
                  Distribuição de Satisfação
                </h2>
                <div className="flex flex-col gap-3">
                  <SatisfactionBar label="Bom" pct={ev.pct_bom} count={ev.count_bom} color="bg-[#00a884]" />
                  <SatisfactionBar label="Neutro" pct={ev.pct_neutro} count={ev.count_neutro} color="bg-amber-400" />
                  <SatisfactionBar label="Ruim" pct={ev.pct_ruim} count={ev.count_ruim} color="bg-red-400" />
                </div>
              </section>
            )}

            {/* Quality scores */}
            {ev && (
              <section className="rounded-2xl border border-black/6 bg-white p-6">
                <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-[#667781]">
                  Métricas Auxiliares
                </h2>
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                  <ScoreGauge
                    label="Esforço do cliente"
                    value={ev.avg_effort}
                    max={5}
                    description="1 = muito baixo · 5 = muito alto"
                  />
                  <ScoreGauge
                    label="Entendimento do objetivo"
                    value={ev.avg_understanding}
                    max={2}
                    description="0 = não entendeu · 2 = entendeu cedo"
                  />
                  <ScoreGauge
                    label="Resolução / avanço útil"
                    value={ev.avg_resolution}
                    max={2}
                    description="0 = sem avanço · 2 = objetivo resolvido"
                  />
                </div>
              </section>
            )}

            {/* Security - Prompt Injection */}
            {ev && (
              <section className="rounded-2xl border border-black/6 bg-white p-6">
                <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-[#667781]">
                  Segurança · Tentativas de Injeção
                </h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div className="flex flex-col gap-1 rounded-2xl border border-black/6 p-5">
                    <span className="text-2xl font-bold tabular-nums text-[#111b21]">
                      {ev.count_injection_detected}
                    </span>
                    <span className="text-xs font-medium uppercase tracking-wider text-[#667781]">
                      Sessões com tentativa detectada
                    </span>
                  </div>
                  <div className="flex flex-col gap-2 rounded-2xl border border-black/6 p-5">
                    <div className="flex items-baseline justify-between">
                      <span className="text-sm font-semibold text-[#111b21]">% do total</span>
                      <span className={`text-xl font-bold tabular-nums ${
                        ev.pct_injection_detected > 5 ? 'text-red-500' : 'text-[#00a884]'
                      }`}>
                        {ev.pct_injection_detected.toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-[#e9edef]">
                      <div
                        className={`h-full rounded-full transition-all ${
                          ev.pct_injection_detected > 5 ? 'bg-red-400' : 'bg-[#00a884]'
                        }`}
                        style={{ width: `${Math.min(ev.pct_injection_detected, 100)}%` }}
                      />
                    </div>
                    <span className="text-xs text-[#667781]">
                      {ev.pct_injection_detected > 5
                        ? '⚠ Nível elevado de tentativas'
                        : '✓ Nível normal'}
                    </span>
                  </div>
                </div>
              </section>
            )}

            {/* Operational metrics */}
            {op && (
              <section>
                <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-[#667781]">
                  Métricas Operacionais
                </h2>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                  <StatCard label="Sessões totais" value={op.total_sessions} />
                  <StatCard label="Mensagens trocadas" value={op.total_messages} />
                  <StatCard label="Hits de RAG" value={op.total_rag_hits} />
                </div>
              </section>
            )}

            {/* Token consumption charts */}
            {tokensReport && (
              <>
                <section className="rounded-2xl border border-black/6 bg-white p-6">
                  <div className="mb-4 flex items-baseline justify-between">
                    <h2 className="text-sm font-semibold uppercase tracking-wider text-[#667781]">
                      Consumo de Tokens · Total por Dia
                    </h2>
                    <span className="text-xs text-[#667781]">
                      Total: {tokensReport.total_tokens.toLocaleString()} tokens
                    </span>
                  </div>
                  <TokensTimeSeriesChart report={tokensReport} />
                </section>

                <section className="rounded-2xl border border-black/6 bg-white p-6">
                  <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-[#667781]">
                    Consumo de Tokens · Por Modelo
                  </h2>
                  <TokensByModelChart report={tokensReport} />
                </section>
              </>
            )}
          </div>
        ) : (
          <div className="mx-auto max-w-5xl">
            <ResultadosUnitariosTab
              sessions={agentSessions}
              loadDetail={loadAgentSessionDetail}
            />
          </div>
        )}
      </div>
    </div>
  )
}
