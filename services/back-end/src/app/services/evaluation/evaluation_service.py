from __future__ import annotations

from app.domain_models.chat.models import ChatSession
from app.domain_models.common.contracts import SessionRepository
from app.domain_models.common.ids import SessionId
from app.domain_models.evaluation.models import EvaluationsSummary, SessionEvaluation
from app.engines.evaluation.evaluations_summary_engine import EvaluationsSummaryEngine
from app.engines.evaluation.session_evaluation_engine import SessionEvaluationEngine


class EvaluationService:
    def __init__(
        self,
        session_repository: SessionRepository,
        evaluation_engine: SessionEvaluationEngine,
        evaluations_summary_engine: EvaluationsSummaryEngine,
    ) -> None:
        self._session_repository = session_repository
        self._evaluation_engine = evaluation_engine
        self._evaluations_summary_engine = evaluations_summary_engine

    def evaluate_session(self, session_id: SessionId) -> SessionEvaluation:
        session = self._session_repository.find_by_id(session_id)
        return self._evaluate(session)

    def list_all_evaluations(self) -> tuple[SessionEvaluation, ...]:
        sessions = self._session_repository.list_all()
        return tuple(self._evaluate(session) for session in sessions)

    def evaluations_summary(self) -> EvaluationsSummary:
        evaluations = self.list_all_evaluations()
        return self._evaluations_summary_engine.build_summary(evaluations)

    def _evaluate(self, session: ChatSession) -> SessionEvaluation:
        return self._evaluation_engine.evaluate(session)
