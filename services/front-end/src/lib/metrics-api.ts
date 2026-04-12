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
  count_injection_detected: number
  pct_injection_detected: number
  total_tokens_used: number
}

export type MetricsJob = {
  id: number
  job_type: string
  status: 'running' | 'done' | 'error'
  started_at: string
  finished_at: string | null
  session_count: number | null
  object_key: string | null
  processed_count: number | null
  error_message: string | null
}

export type AgentSessionListItem = {
  session_id: string
  satisfaction: string
  objetivo_cliente: string
  total_tokens: number | null
  prompt_injection_detected: boolean
  effort_score: number
  understanding_score: number
  resolution_score: number
  mudanca_comportamental: string | null
  sinal_fechamento: string | null
}

export type AgentSessionMessage = {
  role: string
  content: string
}

export type AgentSessionDetail = {
  session_id: string
  satisfaction: string
  objetivo_cliente: string
  effort_score: number
  understanding_score: number
  resolution_score: number
  mudanca_comportamental: string | null
  sinal_fechamento: string | null
  prompt_tokens: number | null
  completion_tokens: number | null
  total_tokens: number | null
  prompt_injection_detected: boolean
  injection_snippets: string[]
  evidences: string[]
  messages: AgentSessionMessage[]
  prompt_used: string
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, options)
  if (!response.ok) throw new Error('Não foi possível carregar os dados.')
  return (await response.json()) as T
}

async function requestOrNull<T>(path: string): Promise<T | null> {
  const response = await fetch(`${apiBaseUrl}${path}`)
  if (response.status === 404) return null
  if (!response.ok) throw new Error('Não foi possível carregar os dados.')
  return (await response.json()) as T
}

export function getMetricsSummary() {
  return request<MetricsSummary>('/api/metrics/summary')
}

export function getEvaluationsSummary() {
  return request<EvaluationsSummary>('/api/evaluation/summary')
}

export function getLatestExportJob() {
  return requestOrNull<MetricsJob>('/api/metrics/jobs/export/latest')
}

export function getLatestAnalysisJob() {
  return requestOrNull<MetricsJob>('/api/metrics/jobs/analysis/latest')
}

export function exportConversations() {
  return request<{ session_count: number; object_key: string }>('/api/conversations/export', {
    method: 'POST',
  })
}

export async function getCreditBalance(
  apiKey: string,
): Promise<{ available: number; checked_at: string }> {
  const response = await fetch(`${apiBaseUrl}/api/credits/balance`, {
    headers: { 'x-api-key': apiKey },
  })
  if (!response.ok) throw new Error('Não foi possível carregar o saldo de créditos.')
  return (await response.json()) as { available: number; checked_at: string }
}

export function runAgentAnalysis(apiKey: string, modelId?: string) {
  return request<unknown>('/api/evaluation/agent-analysis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey, model_id: modelId ?? null }),
  })
}

export function getAgentSessions() {
  return request<AgentSessionListItem[]>('/api/evaluation/agent-sessions')
}

export function getAgentSessionDetail(sessionId: string) {
  return request<AgentSessionDetail>(`/api/evaluation/agent-sessions/${sessionId}`)
}
