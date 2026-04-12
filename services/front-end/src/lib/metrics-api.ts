const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? 'http://0.0.0.0:8000').replace(/\/$/, '')

export type MetricsSummary = {
  total_sessions: number
  total_messages: number
  total_rag_hits: number
}

export type EvaluationsSummary = {
  total_evaluated: number
  count_bom: number
  count_neutro: number
  count_ruim: number
  pct_bom: number
  pct_neutro: number
  pct_ruim: number
  indice_ia_operadora: number
  avg_effort: number
  avg_understanding: number
  avg_resolution: number
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`)
  if (!response.ok) throw new Error('Não foi possível carregar os dados.')
  return (await response.json()) as T
}

export function getMetricsSummary() {
  return request<MetricsSummary>('/api/metrics/summary')
}

export function getEvaluationsSummary() {
  return request<EvaluationsSummary>('/api/evaluation/summary')
}
