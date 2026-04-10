from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class SessionId:
    value: UUID

    @classmethod
    def new(cls) -> "SessionId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class MessageId:
    value: UUID

    @classmethod
    def new(cls) -> "MessageId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class AgentRunId:
    value: UUID

    @classmethod
    def new(cls) -> "AgentRunId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class DocumentId:
    value: UUID

    @classmethod
    def new(cls) -> "DocumentId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)
