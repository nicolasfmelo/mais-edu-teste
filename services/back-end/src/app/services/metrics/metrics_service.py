from __future__ import annotations

from app.domain_models.common.contracts import MetricsRepository
from app.domain_models.metrics.models import ConversationMetrics, MetricsSummary, TokensReport
from app.engines.metrics.metrics_summary_engine import MetricsSummaryEngine


class MetricsService:
    def __init__(
        self,
        metrics_repository: MetricsRepository,
        summary_engine: MetricsSummaryEngine,
    ) -> None:
        self._metrics_repository = metrics_repository
        self._summary_engine = summary_engine

    def record(self, metrics: ConversationMetrics) -> None:
        self._metrics_repository.save(metrics)

    def summary(self) -> MetricsSummary:
        return self._summary_engine.build_summary(self._metrics_repository.list_all())

    def tokens_report(self) -> TokensReport:
        return self._summary_engine.build_tokens_report(self._metrics_repository.list_all())
