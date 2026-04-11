from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class ChatSession:
    id: SessionId
    messages: tuple[ChatMessage, ...] = field(default_factory=tuple)

    def append(self, message: ChatMessage) -> "ChatSession":
        return ChatSession(id=self.id, messages=(*self.messages, message))


@dataclass(frozen=True)
class ChatRequest:
    session_id: SessionId
    message: ChatMessage
    api_key: str
    model_id: str | None = None
    system_prompt: str | None = None


@dataclass(frozen=True)
class ChatResponse:
    session_id: SessionId
    reply: ChatMessage
