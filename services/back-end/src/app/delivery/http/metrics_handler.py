from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.domain_models.common.contracts import MetricsJobRepository
from app.domain_models.metrics.job_models import MetricsJobType
from app.delivery.schemas.metrics_schemas import HealthResponseSchema, MetricsJobResponseSchema, MetricsSummaryResponseSchema, TokensReportResponseSchema
from app.services.metrics.metrics_service import MetricsService


class MetricsHandler:
    def __init__(self, metrics_service: MetricsService, metrics_job_repository: MetricsJobRepository) -> None:
        self._metrics_service = metrics_service
        self._metrics_job_repository = metrics_job_repository
        self.router = APIRouter(prefix="/api/metrics", tags=["metrics"])
        self.router.add_api_route("/health", self.health, methods=["GET"], response_model=HealthResponseSchema)
        self.router.add_api_route("/summary", self.summary, methods=["GET"], response_model=MetricsSummaryResponseSchema)
        self.router.add_api_route("/tokens-report", self.tokens_report, methods=["GET"], response_model=TokensReportResponseSchema)
        self.router.add_api_route(
            "/jobs/export/latest",
            self.latest_export_job,
            methods=["GET"],
            response_model=MetricsJobResponseSchema,
        )
        self.router.add_api_route(
            "/jobs/analysis/latest",
            self.latest_analysis_job,
            methods=["GET"],
            response_model=MetricsJobResponseSchema,
        )

    async def health(self) -> HealthResponseSchema:
        return HealthResponseSchema(status="ok")

    async def summary(self) -> MetricsSummaryResponseSchema:
        return MetricsSummaryResponseSchema.from_domain(self._metrics_service.summary())

    async def tokens_report(self) -> TokensReportResponseSchema:
        return TokensReportResponseSchema.from_domain(self._metrics_service.tokens_report())

    async def latest_export_job(self) -> MetricsJobResponseSchema:
        job = self._metrics_job_repository.get_latest_job(MetricsJobType.EXPORT)
        if job is None:
            raise HTTPException(status_code=404, detail="No export job found.")
        return MetricsJobResponseSchema.from_domain(job)

    async def latest_analysis_job(self) -> MetricsJobResponseSchema:
        job = self._metrics_job_repository.get_latest_job(MetricsJobType.ANALYSIS)
        if job is None:
            raise HTTPException(status_code=404, detail="No analysis job found.")
        return MetricsJobResponseSchema.from_domain(job)
