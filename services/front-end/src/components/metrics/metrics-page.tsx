import { useMetricsPage } from '@/hooks/use-metrics-page'

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

export function MetricsPage() {
  const { metricsSummary, evaluationsSummary, isLoading, error } = useMetricsPage()

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <span className="text-sm text-[#667781]">Carregando métricas…</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <span className="text-sm text-red-500">{error}</span>
      </div>
    )
  }

  const ev = evaluationsSummary
  const op = metricsSummary

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="mx-auto flex max-w-4xl flex-col gap-6">

        {/* Header */}
        <div>
          <h1 className="text-xl font-bold text-[#111b21]">Métricas da IA Operadora</h1>
          <p className="mt-1 text-sm text-[#667781]">Avaliação de qualidade percebida pelo cliente</p>
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
                <span className="text-xs text-[#667781]">avaliações heurísticas</span>
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
      </div>
    </div>
  )
}
