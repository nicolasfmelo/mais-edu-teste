from __future__ import annotations

from app.domain_models.metrics.models import ConversationMetrics


class InMemoryMetricsRepository:
    def __init__(self) -> None:
        self._items: list[ConversationMetrics] = []

    def save(self, metrics: ConversationMetrics) -> None:
        self._items.append(metrics)

    def list_all(self) -> tuple[ConversationMetrics, ...]:
        return tuple(self._items)
