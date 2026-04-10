from __future__ import annotations

from dataclasses import dataclass

from app.domain_models.common.ids import SessionId


@dataclass(frozen=True)
class ConversationMetrics:
    session_id: SessionId
    messages_count: int
    rag_hits: int
    used_credit_check: bool


@dataclass(frozen=True)
class MetricsSummary:
    total_sessions: int
    total_messages: int
    total_rag_hits: int
