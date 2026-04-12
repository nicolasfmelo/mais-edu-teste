import { useEffect, useState } from 'react'
import { getEvaluationsSummary, getMetricsSummary, type EvaluationsSummary, type MetricsSummary } from '@/lib/metrics-api'

export type MetricsPageData = {
  metricsSummary: MetricsSummary | null
  evaluationsSummary: EvaluationsSummary | null
  isLoading: boolean
  error: string | null
}

export function useMetricsPage(): MetricsPageData {
  const [metricsSummary, setMetricsSummary] = useState<MetricsSummary | null>(null)
  const [evaluationsSummary, setEvaluationsSummary] = useState<EvaluationsSummary | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const [metrics, evaluations] = await Promise.all([getMetricsSummary(), getEvaluationsSummary()])
        if (cancelled) return
        setMetricsSummary(metrics)
        setEvaluationsSummary(evaluations)
      } catch {
        if (!cancelled) setError('Não foi possível carregar as métricas.')
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [])

  return { metricsSummary, evaluationsSummary, isLoading, error }
}
