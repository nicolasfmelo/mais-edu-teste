from __future__ import annotations

from app.domain_models.agent.models import AgentInvocation, AgentReply
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
            invocation=AgentInvocation(
                session_id=chat_request.session_id,
                api_key=chat_request.api_key,
                idempotency_key=f"chat-{chat_request.session_id.value}-{chat_request.message.id.value}",
                latest_user_message=chat_request.message.content,
                conversation_messages=session_with_user_message.messages,
                model_id=chat_request.model_id,
                system_prompt=chat_request.system_prompt,
            ),
        )

        assistant_message = self._create_assistant_message(agent_reply)
        persisted_session = self._session_repository.save(session_with_user_message.append(assistant_message))

        self._metrics_service.record(
            ConversationMetrics(
                session_id=persisted_session.id,
                messages_count=len(persisted_session.messages),
                rag_hits=len(agent_reply.retrieved_chunks),
                used_credit_check=len(persisted_session.messages) <= 2,
            )
        )

        return ChatResponse(session_id=persisted_session.id, reply=persisted_session.messages[-1])

    def get_session(self, session_id: SessionId) -> ChatSession:
        return self._session_repository.find_by_id(session_id)

    def list_sessions(self) -> tuple[ChatSession, ...]:
        return self._session_repository.list_all()

    def create_session(self) -> ChatSession:
        return self._session_repository.save(ChatSession(id=SessionId.new()))

    def _create_assistant_message(self, agent_reply: AgentReply) -> ChatMessage:
        return ChatMessage(
            id=MessageId.new(),
            role=MessageRole.ASSISTANT,
            content=agent_reply.content,
        )
