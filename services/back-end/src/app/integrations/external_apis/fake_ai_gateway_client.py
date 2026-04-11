from __future__ import annotations

from app.domain_models.agent.models import GatewayPromptReply, GatewayPromptRequest


class FakeAIGatewayClient:
    def generate_reply(self, request: GatewayPromptRequest) -> GatewayPromptReply:
        return GatewayPromptReply(
            content=f"Resposta inicial para: {request.prompt[:160]}",
            model_id=request.model_id,
        )
