from __future__ import annotations

from collections import defaultdict

from app.domain_models.metrics.models import (
    ConversationMetrics,
    MetricsSummary,
    ModelTokenEntry,
    TokenEntry,
    TokensReport,
)


class MetricsSummaryEngine:
    """Pure aggregation rules for operational metrics."""

    def build_summary(self, metrics_records: tuple[ConversationMetrics, ...]) -> MetricsSummary:
        return MetricsSummary(
            total_sessions=len(metrics_records),
            total_messages=sum(record.messages_count for record in metrics_records),
            total_rag_hits=sum(record.rag_hits for record in metrics_records),
        )

    def build_tokens_report(self, metrics_records: tuple[ConversationMetrics, ...]) -> TokensReport:
        total_tokens = sum(record.tokens_used for record in metrics_records)

        by_date: dict[str, int] = defaultdict(int)
        by_model: dict[str, int] = defaultdict(int)

        for record in metrics_records:
            date_key = record.created_at.strftime("%Y-%m-%d") if record.created_at else "desconhecido"
            by_date[date_key] += record.tokens_used
            model_key = record.model_id or "desconhecido"
            by_model[model_key] += record.tokens_used

        time_series = tuple(
            TokenEntry(date=date, tokens=tokens)
            for date, tokens in sorted(by_date.items())
        )
        by_model_entries = tuple(
            ModelTokenEntry(model_id=model, tokens=tokens)
            for model, tokens in sorted(by_model.items(), key=lambda x: x[1], reverse=True)
        )

        return TokensReport(
            total_tokens=total_tokens,
            time_series=time_series,
            by_model=by_model_entries,
        )
