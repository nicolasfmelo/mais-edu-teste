from __future__ import annotations

from app.domain_models.agent.models import AgentReply
from app.domain_models.common.ids import AgentRunId
from app.domain_models.rag.models import RetrievedChunk


class FakeAIGatewayClient:
    def generate_reply(self, prompt: str, context: tuple[RetrievedChunk, ...]) -> AgentReply:
        context_hint = context[0].content[:80] if context else "sem contexto recuperado"
        return AgentReply(
            run_id=AgentRunId.new(),
            content=f"Resposta inicial para: {prompt}. Contexto: {context_hint}",
            retrieved_chunks=context,
        )
