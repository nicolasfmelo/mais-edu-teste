from __future__ import annotations

from app.domain_models.metrics.models import ConversationMetrics, MetricsSummary


class MetricsSummaryEngine:
    """Pure aggregation rules for operational metrics."""

    def build_summary(self, metrics_records: tuple[ConversationMetrics, ...]) -> MetricsSummary:
        return MetricsSummary(
            total_sessions=len(metrics_records),
            total_messages=sum(record.messages_count for record in metrics_records),
            total_rag_hits=sum(record.rag_hits for record in metrics_records),
        )
