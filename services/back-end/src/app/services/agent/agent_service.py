from __future__ import annotations

from app.domain_models.agent.models import AgentDecision, AgentReply
from app.domain_models.chat.models import ChatSession
from app.domain_models.common.contracts import AIGatewayClient, CreditSystemClient
from app.domain_models.common.ids import AgentRunId
from app.domain_models.rag.models import RagQuery
from app.services.rag.rag_service import RagService


class AgentService:
    def __init__(
        self,
        rag_service: RagService,
        ai_gateway_client: AIGatewayClient,
        credit_system_client: CreditSystemClient,
    ) -> None:
        self._rag_service = rag_service
        self._ai_gateway_client = ai_gateway_client
        self._credit_system_client = credit_system_client

    def generate_reply(self, session: ChatSession, latest_user_message: str) -> AgentReply:
        decision = AgentDecision(
            should_use_rag=True,
            should_call_credit_system=len(session.messages) == 1,
        )

        if decision.should_call_credit_system:
            self._credit_system_client.verify_credit(session.id)

        retrieved_chunks = self._rag_service.retrieve(
            RagQuery(session_id=session.id, question=latest_user_message)
        ) if decision.should_use_rag else tuple()

        gateway_reply = self._ai_gateway_client.generate_reply(
            prompt=latest_user_message,
            context=retrieved_chunks,
        )

        return AgentReply(
            run_id=AgentRunId.new(),
            content=gateway_reply.content,
            retrieved_chunks=retrieved_chunks,
        )
