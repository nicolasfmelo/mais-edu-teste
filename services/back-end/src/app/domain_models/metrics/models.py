from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.domain_models.common.ids import SessionId


@dataclass(frozen=True)
class ConversationMetrics:
    session_id: SessionId
    messages_count: int
    rag_hits: int
    used_credit_check: bool
    tokens_used: int = 0
    model_id: str | None = None
    created_at: datetime | None = None


@dataclass(frozen=True)
class MetricsSummary:
    total_sessions: int
    total_messages: int
    total_rag_hits: int


@dataclass(frozen=True)
class TokenEntry:
    date: str
    tokens: int


@dataclass(frozen=True)
class ModelTokenEntry:
    model_id: str
    tokens: int


@dataclass(frozen=True)
class TokensReport:
    total_tokens: int
    time_series: tuple[TokenEntry, ...]
    by_model: tuple[ModelTokenEntry, ...]
