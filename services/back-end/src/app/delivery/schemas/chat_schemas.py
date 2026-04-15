from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain_models.chat.models import ChatAudioResponse, ChatMessage, ChatRequest, ChatResponse, ChatSession, MessageRole
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


class ChatSessionMessageSchema(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, message: ChatMessage) -> "ChatSessionMessageSchema":
        return cls(
            id=message.id.value,
            role=message.role.value,
            content=message.content,
            created_at=message.created_at,
        )


class ChatMessageResponseSchema(BaseModel):
    session_id: UUID
    reply: str
    assistant_message: ChatSessionMessageSchema

    @classmethod
    def from_domain(cls, response: ChatResponse) -> "ChatMessageResponseSchema":
        return cls(
            session_id=response.session_id.value,
            reply=response.reply.content,
            assistant_message=ChatSessionMessageSchema.from_domain(response.reply),
        )


class ChatAudioMessageResponseSchema(ChatMessageResponseSchema):
    transcription: str

    @classmethod
    def from_domain(cls, response: ChatAudioResponse) -> "ChatAudioMessageResponseSchema":
        return cls(
            session_id=response.session_id.value,
            reply=response.reply.content,
            assistant_message=ChatSessionMessageSchema.from_domain(response.reply),
            transcription=response.transcription,
        )


class ChatSessionSummarySchema(BaseModel):
    id: UUID
    status: str
    display_name: str
    preview: str
    message_count: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_message_at: datetime | None = None

    @classmethod
    def from_domain(cls, session: ChatSession) -> "ChatSessionSummarySchema":
        first_user_message = next(
            (message.content.strip() for message in session.messages if message.role == MessageRole.USER and message.content.strip()),
            "",
        )
        display_name = first_user_message[:40].rstrip()
        if len(first_user_message) > 40:
            display_name = f"{display_name}..."
        if not display_name:
            display_name = f"Sessao {str(session.id.value)[:8]}"

        preview = session.messages[-1].content if session.messages else "Nova conversa iniciada."

        return cls(
            id=session.id.value,
            status=session.status,
            display_name=display_name,
            preview=preview,
            message_count=len(session.messages),
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_message_at=session.last_message_at,
        )


class ChatSessionListResponseSchema(BaseModel):
    items: list[ChatSessionSummarySchema]

    @classmethod
    def from_domain(cls, sessions: tuple[ChatSession, ...]) -> "ChatSessionListResponseSchema":
        return cls(items=[ChatSessionSummarySchema.from_domain(session) for session in sessions])


class ChatSessionDetailResponseSchema(BaseModel):
    session: ChatSessionSummarySchema
    messages: list[ChatSessionMessageSchema]

    @classmethod
    def from_domain(cls, session: ChatSession) -> "ChatSessionDetailResponseSchema":
        return cls(
            session=ChatSessionSummarySchema.from_domain(session),
            messages=[ChatSessionMessageSchema.from_domain(message) for message in session.messages],
        )
