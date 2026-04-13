from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.domain_models.chat.models import ChatSession
from app.domain_models.common.ids import SessionId


class SatisfactionClass(str, Enum):
    BAD = "ruim"
    NEUTRAL = "neutro"
    GOOD = "bom"


class BehaviorChange(str, Enum):
    POSITIVE = "positiva"
    NEUTRAL = "neutra"
    NEGATIVE = "negativa"


class ClosingSignal(str, Enum):
    POSITIVE = "positivo"
    NEUTRAL = "neutro"
    NEGATIVE = "negativo"


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class EvaluationEvidence:
    snippet: str


@dataclass(frozen=True)
class ExportedConversationMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ExportedConversationSession:
    session_id: SessionId
    messages: tuple[ExportedConversationMessage, ...] = field(default_factory=tuple)

    @classmethod
    def from_chat_session(cls, session: ChatSession) -> "ExportedConversationSession":
        return cls(
            session_id=session.id,
            messages=tuple(
                ExportedConversationMessage(role=message.role.value, content=message.content)
                for message in session.messages
            ),
        )


@dataclass(frozen=True)
class ParsedAnalysisResponse:
    objetivo_cliente: str
    satisfaction: SatisfactionClass
    effort_score: int
    understanding_score: int
    resolution_score: int
    behavior_change: BehaviorChange
    closing_signal: ClosingSignal
    evidences: tuple[EvaluationEvidence, ...] = field(default_factory=tuple)
    injection_attempt: bool = False
    injection_evidence: str | None = None


@dataclass(frozen=True)
class SessionEvaluation:
    session_id: SessionId
    satisfaction: SatisfactionClass
    effort_score: int
    understanding_score: int
    resolution_score: int
    evidences: tuple[EvaluationEvidence, ...] = field(default_factory=tuple)
    objetivo_cliente: str = ""
    mudanca_comportamental: BehaviorChange | None = None
    sinal_fechamento: ClosingSignal | None = None
    token_usage: TokenUsage | None = None
    prompt_injection_detected: bool = False
    injection_snippets: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvaluationsSummary:
    total_evaluated: int
    count_bom: int
    count_neutro: int
    count_ruim: int
    pct_bom: float
    pct_neutro: float
    pct_ruim: float
    indice_ia_operadora: float  # % bom - % ruim
    avg_effort: float  # 1–5
    avg_understanding: float  # 0–2
    avg_resolution: float  # 0–2
    total_tokens_used: int = 0
    count_mudanca_positiva: int = 0
    count_mudanca_neutra: int = 0
    count_mudanca_negativa: int = 0
    count_injection_detected: int = 0
    pct_injection_detected: float = 0.0


@dataclass(frozen=True)
class ConversationAnalysisResult:
    evaluations: tuple[SessionEvaluation, ...]
    summary: EvaluationsSummary
