from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.domain_models.common.ids import MessageId, SessionId


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ChatMessage:
    id: MessageId
    role: MessageRole
    content: str
    created_at: datetime | None = None


@dataclass(frozen=True)
class ChatSession:
    id: SessionId
    messages: tuple[ChatMessage, ...] = field(default_factory=tuple)
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_message_at: datetime | None = None

    def append(self, message: ChatMessage) -> "ChatSession":
        return ChatSession(
            id=self.id,
            messages=(*self.messages, message),
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_message_at=self.last_message_at,
        )


@dataclass(frozen=True)
class ChatRequest:
    session_id: SessionId
    message: ChatMessage
    api_key: str
    model_id: str | None = None
    system_prompt: str | None = None


@dataclass(frozen=True)
class ChatAudioRequest:
    session_id: SessionId
    audio_bytes: bytes
    audio_filename: str
    api_key: str
    audio_content_type: str | None = None
    language: str | None = None
    model_id: str | None = None
    system_prompt: str | None = None


@dataclass(frozen=True)
class ChatResponse:
    session_id: SessionId
    reply: ChatMessage


@dataclass(frozen=True)
class ChatAudioResponse:
    session_id: SessionId
    transcription: str
    reply: ChatMessage
