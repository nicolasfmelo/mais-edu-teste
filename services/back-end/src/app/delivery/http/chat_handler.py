from __future__ import annotations

from fastapi import APIRouter

from app.delivery.schemas.chat_schemas import ChatMessageRequestSchema, ChatMessageResponseSchema
from app.services.chat.chat_service import ChatService


class ChatHandler:
    def __init__(self, chat_service: ChatService) -> None:
        self._chat_service = chat_service
        self.router = APIRouter(prefix="/api/chat", tags=["chat"])
        self.router.add_api_route("/messages", self.post_message, methods=["POST"], response_model=ChatMessageResponseSchema)

    async def post_message(self, body: ChatMessageRequestSchema) -> ChatMessageResponseSchema:
        response = self._chat_service.handle_message(body.to_domain())
        return ChatMessageResponseSchema.from_domain(response)
