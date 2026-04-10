from __future__ import annotations

from fastapi import APIRouter

from app.delivery.schemas.metrics_schemas import HealthResponseSchema, MetricsSummaryResponseSchema
from app.services.metrics.metrics_service import MetricsService


class MetricsHandler:
    def __init__(self, metrics_service: MetricsService) -> None:
        self._metrics_service = metrics_service
        self.router = APIRouter(prefix="/api/metrics", tags=["metrics"])
        self.router.add_api_route("/health", self.health, methods=["GET"], response_model=HealthResponseSchema)
        self.router.add_api_route("/summary", self.summary, methods=["GET"], response_model=MetricsSummaryResponseSchema)

    async def health(self) -> HealthResponseSchema:
        return HealthResponseSchema(status="ok")

    async def summary(self) -> MetricsSummaryResponseSchema:
        return MetricsSummaryResponseSchema.from_domain(self._metrics_service.summary())
