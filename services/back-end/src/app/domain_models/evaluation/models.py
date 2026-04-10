from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from app.domain_models.common.ids import SessionId


class SatisfactionClass(str, Enum):
    BAD = "ruim"
    NEUTRAL = "neutro"
    GOOD = "bom"


@dataclass(frozen=True)
class EvaluationEvidence:
    snippet: str


@dataclass(frozen=True)
class SessionEvaluation:
    session_id: SessionId
    satisfaction: SatisfactionClass
    effort_score: int
    understanding_score: int
    resolution_score: int
    evidences: tuple[EvaluationEvidence, ...] = field(default_factory=tuple)
