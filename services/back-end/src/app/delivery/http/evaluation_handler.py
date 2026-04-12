from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from app.delivery.schemas.evaluation_schemas import EvaluationsSummaryResponseSchema, SessionEvaluationResponseSchema
from app.domain_models.common.ids import SessionId
from app.services.evaluation.evaluation_service import EvaluationService


class EvaluationHandler:
    def __init__(self, evaluation_service: EvaluationService) -> None:
        self._evaluation_service = evaluation_service
        self.router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])
        self.router.add_api_route(
            "/sessions/{session_id}",
            self.evaluate_session,
            methods=["POST"],
            response_model=SessionEvaluationResponseSchema,
        )
        self.router.add_api_route(
            "/summary",
            self.evaluations_summary,
            methods=["GET"],
            response_model=EvaluationsSummaryResponseSchema,
        )

    async def evaluate_session(self, session_id: UUID) -> SessionEvaluationResponseSchema:
        evaluation = self._evaluation_service.evaluate_session(SessionId(value=session_id))
        return SessionEvaluationResponseSchema.from_domain(evaluation)

    async def evaluations_summary(self) -> EvaluationsSummaryResponseSchema:
        summary = self._evaluation_service.evaluations_summary()
        return EvaluationsSummaryResponseSchema.from_domain(summary)
