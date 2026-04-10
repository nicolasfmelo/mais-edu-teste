from __future__ import annotations

from app.domain_models.chat.models import ChatSession
from app.domain_models.common.contracts import SessionRepository
from app.domain_models.common.ids import SessionId
from app.domain_models.evaluation.models import SessionEvaluation
from app.engines.evaluation.session_evaluation_engine import SessionEvaluationEngine


class EvaluationService:
    def __init__(
        self,
        session_repository: SessionRepository,
        evaluation_engine: SessionEvaluationEngine,
    ) -> None:
        self._session_repository = session_repository
        self._evaluation_engine = evaluation_engine

    def evaluate_session(self, session_id: SessionId) -> SessionEvaluation:
        session = self._session_repository.find_by_id(session_id)
        return self._evaluate(session)

    def _evaluate(self, session: ChatSession) -> SessionEvaluation:
        return self._evaluation_engine.evaluate(session)
