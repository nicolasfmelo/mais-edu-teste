import { useCallback, useEffect, useState } from 'react'
import {
  exportConversations,
  getAgentSessionDetail,
  getAgentSessions,
  getEvaluationsSummary,
  getLatestAnalysisJob,
  getLatestExportJob,
  getMetricsSummary,
  getTokensReport,
  runAgentAnalysis,
  type AgentSessionDetail,
  type AgentSessionListItem,
  type EvaluationsSummary,
  type MetricsJob,
  type MetricsSummary,
  type TokensReport,
} from '@/lib/metrics-api'

export type MetricsPageData = {
  metricsSummary: MetricsSummary | null
  evaluationsSummary: EvaluationsSummary | null
  exportJob: MetricsJob | null
  analysisJob: MetricsJob | null
  agentSessions: AgentSessionListItem[]
  tokensReport: TokensReport | null
  isLoading: boolean
  isSyncing: boolean
  isAnalyzing: boolean
  error: string | null
  syncConversations: () => Promise<void>
  runAnalysis: () => Promise<void>
  loadAgentSessionDetail: (sessionId: string) => Promise<AgentSessionDetail>
}

export function useMetricsPage(apiKey: string): MetricsPageData {
  const [metricsSummary, setMetricsSummary] = useState<MetricsSummary | null>(null)
  const [evaluationsSummary, setEvaluationsSummary] = useState<EvaluationsSummary | null>(null)
  const [exportJob, setExportJob] = useState<MetricsJob | null>(null)
  const [analysisJob, setAnalysisJob] = useState<MetricsJob | null>(null)
  const [agentSessions, setAgentSessions] = useState<AgentSessionListItem[]>([])
  const [tokensReport, setTokensReport] = useState<TokensReport | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSyncing, setIsSyncing] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadAll = useCallback(async (cancelled?: { current: boolean }) => {
    setIsLoading(true)
    setError(null)
    try {
      const [metrics, evaluations, exportJobResult, analysisJobResult, sessions, tokens] = await Promise.all([
        getMetricsSummary(),
        getEvaluationsSummary(),
        getLatestExportJob(),
        getLatestAnalysisJob(),
        getAgentSessions(),
        getTokensReport(),
      ])
      if (cancelled?.current) return
      setMetricsSummary(metrics)
      setEvaluationsSummary(evaluations)
      setExportJob(exportJobResult)
      setAnalysisJob(analysisJobResult)
      setAgentSessions(sessions)
      setTokensReport(tokens)
    } catch {
      if (!cancelled?.current) setError('Não foi possível carregar as métricas.')
    } finally {
      if (!cancelled?.current) setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    const cancelled = { current: false }
    void loadAll(cancelled)
    return () => {
      cancelled.current = true
    }
  }, [loadAll])

  const syncConversations = useCallback(async () => {
    setIsSyncing(true)
    setError(null)
    try {
      await exportConversations()
      const job = await getLatestExportJob()
      setExportJob(job)
    } catch {
      setError('Falha ao sincronizar conversas com o MinIO.')
    } finally {
      setIsSyncing(false)
    }
  }, [])

  const runAnalysis = useCallback(async () => {
    if (!apiKey.trim()) {
      setError('Configure a API Key no painel do chat antes de rodar a análise.')
      return
    }
    setIsAnalyzing(true)
    setError(null)
    try {
      await runAgentAnalysis(apiKey.trim())
      const [evaluations, job, sessions] = await Promise.all([
        getEvaluationsSummary(),
        getLatestAnalysisJob(),
        getAgentSessions(),
      ])
      setEvaluationsSummary(evaluations)
      setAnalysisJob(job)
      setAgentSessions(sessions)
    } catch {
      setError('Falha ao executar a análise do agente.')
    } finally {
      setIsAnalyzing(false)
    }
  }, [apiKey])

  const loadAgentSessionDetail = useCallback(
    (sessionId: string) => getAgentSessionDetail(sessionId),
    [],
  )

  return {
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
  }
}
