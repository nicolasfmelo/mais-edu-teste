from __future__ import annotations

from pydantic import BaseModel

from app.domain_models.metrics.models import MetricsSummary


class HealthResponseSchema(BaseModel):
    status: str


class MetricsSummaryResponseSchema(BaseModel):
    total_sessions: int
    total_messages: int
    total_rag_hits: int

    @classmethod
    def from_domain(cls, summary: MetricsSummary) -> "MetricsSummaryResponseSchema":
        return cls(
            total_sessions=summary.total_sessions,
            total_messages=summary.total_messages,
            total_rag_hits=summary.total_rag_hits,
        )
