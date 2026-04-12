from __future__ import annotations

from app.domain_models.agent.models import AgentInvocation, GatewayPromptRequest, InstitutionProfile
from app.domain_models.chat.models import ChatMessage, MessageRole
from app.domain_models.rag.models import RetrievedChunk


class PromptAssemblyEngine:
    def __init__(self, institution_profile: InstitutionProfile) -> None:
        self._institution_profile = institution_profile

    def build_gateway_request(
        self,
        invocation: AgentInvocation,
        retrieved_chunks: tuple[RetrievedChunk, ...],
    ) -> GatewayPromptRequest:
        sections: list[str] = []

        sections.append(
            "PERFIL INSTITUCIONAL E DA AGENTE:\n"
            f"Instituicao: {self._institution_profile.institution_name}\n"
            f"Agente: {self._institution_profile.agent_name}\n"
            f"Exemplo de apresentacao: {self._institution_profile.presentation_example}\n"
            f"Briefing completo:\n{self._institution_profile.briefing_markdown.strip()}"
        )

        if invocation.system_prompt:
            sections.append(f"SISTEMA:\n{invocation.system_prompt.strip()}")

        if self._is_first_turn(invocation.conversation_messages):
            sections.append(
                "INSTRUCAO DE ABERTURA:\n"
                f"Esta e a primeira resposta da conversa. Cumprimente o aluno e se apresente como "
                f"{self._institution_profile.agent_name}, assistente virtual do "
                f"{self._institution_profile.institution_name}, antes de orientar a resposta."
            )

        history = self._render_history(invocation.conversation_messages)
        if history:
            sections.append(f"HISTORICO DA CONVERSA:\n{history}")

        context = self._render_context(retrieved_chunks)
        if context:
            sections.append(f"CONTEXTO RECUPERADO:\n{context}")

        sections.append(f"PERGUNTA ATUAL DO USUARIO:\n{invocation.latest_user_message.strip()}")
        sections.append(
            "INSTRUCAO DE RESPOSTA:\n"
            "Responda em portugues do Brasil, de forma objetiva, util e orientada ao aluno."
        )

        return GatewayPromptRequest(
            api_key=invocation.api_key,
            idempotency_key=invocation.idempotency_key,
            prompt="\n\n".join(section for section in sections if section),
            model_id=invocation.model_id,
        )

    def _render_history(self, messages: tuple[ChatMessage, ...]) -> str:
        relevant_messages = messages[-6:]
        rendered = []
        for message in relevant_messages:
            if message.role == MessageRole.SYSTEM:
                continue
            speaker = "usuario" if message.role == MessageRole.USER else "assistente"
            rendered.append(f"- {speaker}: {message.content.strip()}")
        return "\n".join(rendered)

    def _render_context(self, retrieved_chunks: tuple[RetrievedChunk, ...]) -> str:
        if not retrieved_chunks:
            return ""
        return "\n".join(f"- {chunk.content.strip()}" for chunk in retrieved_chunks)

    def _is_first_turn(self, messages: tuple[ChatMessage, ...]) -> bool:
        relevant_messages = tuple(message for message in messages if message.role != MessageRole.SYSTEM)
        return len(relevant_messages) <= 1
