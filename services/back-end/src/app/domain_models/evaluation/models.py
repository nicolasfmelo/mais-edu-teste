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
