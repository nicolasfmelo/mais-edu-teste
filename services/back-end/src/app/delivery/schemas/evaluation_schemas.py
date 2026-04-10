from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.domain_models.evaluation.models import SessionEvaluation


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
