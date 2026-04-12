from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain_models.metrics.job_models import MetricsJob
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


class MetricsJobResponseSchema(BaseModel):
    id: int
    job_type: str
    status: str
    started_at: datetime
    finished_at: datetime | None = None
    session_count: int | None = None
    object_key: str | None = None
    processed_count: int | None = None
    error_message: str | None = None

    @classmethod
    def from_domain(cls, job: MetricsJob) -> "MetricsJobResponseSchema":
        return cls(
            id=job.id,
            job_type=job.job_type.value,
            status=job.status.value,
            started_at=job.started_at,
            finished_at=job.finished_at,
            session_count=job.session_count,
            object_key=job.object_key,
            processed_count=job.processed_count,
            error_message=job.error_message,
        )
