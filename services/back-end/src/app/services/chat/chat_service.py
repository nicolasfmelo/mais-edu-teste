from __future__ import annotations

from app.domain_models.agent.models import AgentReply
from app.domain_models.chat.models import ChatMessage, ChatRequest, ChatResponse, ChatSession, MessageRole
from app.domain_models.common.contracts import SessionRepository
from app.domain_models.common.ids import MessageId, SessionId
from app.domain_models.metrics.models import ConversationMetrics
from app.services.agent.agent_service import AgentService
from app.services.metrics.metrics_service import MetricsService


class ChatService:
    def __init__(
        self,
        session_repository: SessionRepository,
        agent_service: AgentService,
        metrics_service: MetricsService,
    ) -> None:
        self._session_repository = session_repository
        self._agent_service = agent_service
        self._metrics_service = metrics_service

    def handle_message(self, chat_request: ChatRequest) -> ChatResponse:
        session = self._session_repository.get_or_create(chat_request.session_id)
        session_with_user_message = session.append(chat_request.message)

        agent_reply = self._agent_service.generate_reply(
            session=session_with_user_message,
            latest_user_message=chat_request.message.content,
        )

        assistant_message = self._create_assistant_message(agent_reply)
        updated_session = session_with_user_message.append(assistant_message)
        self._session_repository.save(updated_session)

        self._metrics_service.record(
            ConversationMetrics(
                session_id=updated_session.id,
                messages_count=len(updated_session.messages),
                rag_hits=len(agent_reply.retrieved_chunks),
                used_credit_check=len(updated_session.messages) <= 2,
            )
        )

        return ChatResponse(session_id=updated_session.id, reply=assistant_message)

    def get_session(self, session_id: SessionId) -> ChatSession:
        return self._session_repository.find_by_id(session_id)

    def _create_assistant_message(self, agent_reply: AgentReply) -> ChatMessage:
        return ChatMessage(
            id=MessageId.new(),
            role=MessageRole.ASSISTANT,
            content=agent_reply.content,
        )
