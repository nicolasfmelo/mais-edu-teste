from __future__ import annotations

from dataclasses import dataclass, field

from app.domain_models.common.ids import AgentRunId
from app.domain_models.rag.models import RetrievedChunk


@dataclass(frozen=True)
class CreditStatus:
    account_name: str
    available: bool


@dataclass(frozen=True)
class AgentDecision:
    should_use_rag: bool
    should_call_credit_system: bool


@dataclass(frozen=True)
class AgentReply:
    run_id: AgentRunId
    content: str
    retrieved_chunks: tuple[RetrievedChunk, ...] = field(default_factory=tuple)
