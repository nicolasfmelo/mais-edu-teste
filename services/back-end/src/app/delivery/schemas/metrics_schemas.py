from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain_models.metrics.job_models import MetricsJob
from app.domain_models.metrics.models import MetricsSummary, ModelTokenEntry, TokenEntry, TokensReport


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


class TokenEntrySchema(BaseModel):
    date: str
    tokens: int

    @classmethod
    def from_domain(cls, entry: TokenEntry) -> "TokenEntrySchema":
        return cls(date=entry.date, tokens=entry.tokens)


class ModelTokenEntrySchema(BaseModel):
    model_id: str
    tokens: int

    @classmethod
    def from_domain(cls, entry: ModelTokenEntry) -> "ModelTokenEntrySchema":
        return cls(model_id=entry.model_id, tokens=entry.tokens)


class TokensReportResponseSchema(BaseModel):
    total_tokens: int
    time_series: list[TokenEntrySchema]
    by_model: list[ModelTokenEntrySchema]

    @classmethod
    def from_domain(cls, report: TokensReport) -> "TokensReportResponseSchema":
        return cls(
            total_tokens=report.total_tokens,
            time_series=[TokenEntrySchema.from_domain(e) for e in report.time_series],
            by_model=[ModelTokenEntrySchema.from_domain(e) for e in report.by_model],
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
