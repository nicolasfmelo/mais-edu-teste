from __future__ import annotations

from fastapi import APIRouter

from app.delivery.schemas.evaluation_schemas import ConversationAnalysisRequestSchema, ConversationAnalysisResponseSchema
from app.services.evaluation.conversation_analysis_service import ConversationAnalysisService


class ConversationAnalysisHandler:
    def __init__(self, conversation_analysis_service: ConversationAnalysisService) -> None:
        self._conversation_analysis_service = conversation_analysis_service
        self.router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])
        self.router.add_api_route(
            "/agent-analysis",
            self.agent_analysis,
            methods=["POST"],
            response_model=ConversationAnalysisResponseSchema,
        )

    async def agent_analysis(self, body: ConversationAnalysisRequestSchema) -> ConversationAnalysisResponseSchema:
        result = self._conversation_analysis_service.analyze_all(
            api_key=body.api_key,
            model_id=body.model_id,
        )
        return ConversationAnalysisResponseSchema.from_domain(result)
