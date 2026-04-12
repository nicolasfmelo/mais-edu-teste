from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter

from app.delivery.schemas.chat_schemas import (
    ChatMessageRequestSchema,
    ChatMessageResponseSchema,
    ChatSessionDetailResponseSchema,
    ChatSessionListResponseSchema,
    ChatSessionSummarySchema,
)
from app.domain_models.common.ids import SessionId
from app.services.chat.chat_service import ChatService


class ChatHandler:
    def __init__(self, chat_service: ChatService) -> None:
        self._chat_service = chat_service
        self.router = APIRouter(prefix="/api/chat", tags=["chat"])
        self.router.add_api_route("/sessions", self.list_sessions, methods=["GET"], response_model=ChatSessionListResponseSchema)
        self.router.add_api_route("/sessions", self.create_session, methods=["POST"], response_model=ChatSessionSummarySchema)
        self.router.add_api_route(
            "/sessions/{session_id}",
            self.get_session,
            methods=["GET"],
            response_model=ChatSessionDetailResponseSchema,
        )
        self.router.add_api_route("/messages", self.post_message, methods=["POST"], response_model=ChatMessageResponseSchema)

    async def list_sessions(self) -> ChatSessionListResponseSchema:
        return ChatSessionListResponseSchema.from_domain(self._chat_service.list_sessions())

    async def create_session(self) -> ChatSessionSummarySchema:
        return ChatSessionSummarySchema.from_domain(self._chat_service.create_session())

    async def get_session(self, session_id: UUID) -> ChatSessionDetailResponseSchema:
        return ChatSessionDetailResponseSchema.from_domain(self._chat_service.get_session(SessionId(value=session_id)))

    async def post_message(self, body: ChatMessageRequestSchema) -> ChatMessageResponseSchema:
        response = self._chat_service.handle_message(body.to_domain())
        return ChatMessageResponseSchema.from_domain(response)
