from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.domain_models.chat.models import ChatMessage, ChatRequest, ChatResponse, MessageRole
from app.domain_models.common.ids import MessageId, SessionId


class ChatMessageRequestSchema(BaseModel):
    session_id: UUID
    message: str = Field(min_length=1)
    api_key: str = Field(min_length=1)
    model_id: str | None = None
    system_prompt: str | None = None

    def to_domain(self) -> ChatRequest:
        return ChatRequest(
            session_id=SessionId(value=self.session_id),
            message=ChatMessage(
                id=MessageId.new(),
                role=MessageRole.USER,
                content=self.message,
            ),
            api_key=self.api_key,
            model_id=self.model_id,
            system_prompt=self.system_prompt,
        )


class ChatMessageResponseSchema(BaseModel):
    session_id: UUID
    reply: str

    @classmethod
    def from_domain(cls, response: ChatResponse) -> "ChatMessageResponseSchema":
        return cls(session_id=response.session_id.value, reply=response.reply.content)
