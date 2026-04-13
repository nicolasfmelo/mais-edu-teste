from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain_models.chat.models import ChatMessage
from app.domain_models.common.ids import AgentRunId, SessionId
from app.domain_models.rag.models import RetrievedChunk


@dataclass(frozen=True)
class CreditBalance:
    available: int
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class AssistantModel:
    key: str
    label: str
    provider: str
    is_default: bool = False
    status: str = "active"


@dataclass(frozen=True)
class CreditStatus:
    account_name: str
    available: bool


@dataclass(frozen=True)
class AgentDecision:
    should_use_rag: bool
    should_call_credit_system: bool


@dataclass(frozen=True)
class InstitutionProfile:
    institution_name: str
    agent_name: str
    presentation_example: str
    briefing_markdown: str


@dataclass(frozen=True)
class AgentInvocation:
    session_id: SessionId
    api_key: str
    idempotency_key: str
    latest_user_message: str
    conversation_messages: tuple[ChatMessage, ...]
    model_id: str | None = None
    system_prompt: str | None = None


@dataclass(frozen=True)
class GatewayPromptRequest:
    api_key: str
    idempotency_key: str
    prompt: str
    model_id: str | None = None


@dataclass(frozen=True)
class GatewayPromptReply:
    content: str
    model_id: str | None = None
    provider_latency_ms: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


@dataclass(frozen=True)
class AgentReply:
    run_id: AgentRunId
    content: str
    retrieved_chunks: tuple[RetrievedChunk, ...] = field(default_factory=tuple)
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    model_id: str | None = None
