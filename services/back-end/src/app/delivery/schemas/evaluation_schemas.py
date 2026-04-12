from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.domain_models.evaluation.models import EvaluationsSummary, SessionEvaluation


class SessionEvaluationResponseSchema(BaseModel):
    session_id: UUID
    satisfaction: str
    effort_score: int
    understanding_score: int
    resolution_score: int
    evidences: list[str]

    @classmethod
    def from_domain(cls, evaluation: SessionEvaluation) -> "SessionEvaluationResponseSchema":
        return cls(
            session_id=evaluation.session_id.value,
            satisfaction=evaluation.satisfaction.value,
            effort_score=evaluation.effort_score,
            understanding_score=evaluation.understanding_score,
            resolution_score=evaluation.resolution_score,
            evidences=[evidence.snippet for evidence in evaluation.evidences],
        )


class EvaluationsSummaryResponseSchema(BaseModel):
    total_evaluated: int
    count_bom: int
    count_neutro: int
    count_ruim: int
    pct_bom: float
    pct_neutro: float
    pct_ruim: float
    indice_ia_operadora: float
    avg_effort: float
    avg_understanding: float
    avg_resolution: float

    @classmethod
    def from_domain(cls, summary: EvaluationsSummary) -> "EvaluationsSummaryResponseSchema":
        return cls(
            total_evaluated=summary.total_evaluated,
            count_bom=summary.count_bom,
            count_neutro=summary.count_neutro,
            count_ruim=summary.count_ruim,
            pct_bom=summary.pct_bom,
            pct_neutro=summary.pct_neutro,
            pct_ruim=summary.pct_ruim,
            indice_ia_operadora=summary.indice_ia_operadora,
            avg_effort=summary.avg_effort,
            avg_understanding=summary.avg_understanding,
            avg_resolution=summary.avg_resolution,
        )
