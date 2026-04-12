from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from app.delivery.schemas.evaluation_schemas import (
    AgentSessionDetailSchema,
    AgentSessionListItemSchema,
    AgentSessionMessageSchema,
    EvaluationsSummaryResponseSchema,
    SessionEvaluationResponseSchema,
)
from app.domain_models.common.exceptions import EvaluationNotFoundError, SessionNotFoundError
from app.domain_models.common.ids import SessionId
from app.services.evaluation.evaluation_service import EvaluationService
from fastapi import HTTPException


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
        self.router.add_api_route(
            "/agent-sessions",
            self.list_agent_sessions,
            methods=["GET"],
            response_model=list[AgentSessionListItemSchema],
        )
        self.router.add_api_route(
            "/agent-sessions/{session_id}",
            self.get_agent_session_detail,
            methods=["GET"],
            response_model=AgentSessionDetailSchema,
        )

    async def evaluate_session(self, session_id: UUID) -> SessionEvaluationResponseSchema:
        evaluation = self._evaluation_service.evaluate_session(SessionId(value=session_id))
        return SessionEvaluationResponseSchema.from_domain(evaluation)

    async def evaluations_summary(self) -> EvaluationsSummaryResponseSchema:
        summary = self._evaluation_service.evaluations_summary()
        return EvaluationsSummaryResponseSchema.from_domain(summary)

    async def list_agent_sessions(self) -> list[AgentSessionListItemSchema]:
        evaluations = self._evaluation_service.list_agent_evaluations()
        return [AgentSessionListItemSchema.from_domain(e) for e in evaluations]

    async def get_agent_session_detail(self, session_id: UUID) -> AgentSessionDetailSchema:
        try:
            evaluation, chat_session, prompt_used = self._evaluation_service.get_agent_session_detail(
                SessionId(value=session_id)
            )
        except EvaluationNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except SessionNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        messages = [
            AgentSessionMessageSchema(
                role=str(msg.role.value if hasattr(msg.role, "value") else msg.role),
                content=msg.content,
            )
            for msg in chat_session.messages
        ]
        return AgentSessionDetailSchema.from_domain(evaluation, messages, prompt_used)
