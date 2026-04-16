from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.domain_models.chat.models import ChatSession, MessageRole
from app.domain_models.common.ids import MessageId, SessionId


@dataclass(frozen=True)
class ConversationExportMessage:
    id: MessageId
    role: MessageRole
    content: str
    created_at: datetime | None = None


@dataclass(frozen=True)
class ConversationExportSession:
    id: SessionId
    status: str
    created_at: datetime | None
    updated_at: datetime | None
    last_message_at: datetime | None
    messages: tuple[ConversationExportMessage, ...] = field(default_factory=tuple)

    @classmethod
    def from_chat_session(cls, session: ChatSession) -> "ConversationExportSession":
        return cls(
            id=session.id,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            last_message_at=session.last_message_at,
            messages=tuple(
                ConversationExportMessage(
                    id=message.id,
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in session.messages
            ),
        )


@dataclass(frozen=True)
class ConversationExportPayload:
    exported_at: datetime
    sessions: tuple[ConversationExportSession, ...] = field(default_factory=tuple)

    @property
    def session_count(self) -> int:
        return len(self.sessions)


@dataclass(frozen=True)
class ConversationExportResult:
    object_key: str
    session_count: int
    exported_at: datetime
