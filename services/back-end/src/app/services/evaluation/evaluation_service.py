from __future__ import annotations

from app.domain_models.chat.models import ChatSession
from app.domain_models.common.contracts import AgentEvaluationRepository, SessionRepository
from app.domain_models.common.exceptions import EvaluationNotFoundError
from app.domain_models.common.ids import SessionId
from app.domain_models.evaluation.models import EvaluationsSummary, SessionEvaluation
from app.engines.evaluation.conversation_analysis_prompt_engine import build_analysis_prompt
from app.engines.evaluation.evaluations_summary_engine import EvaluationsSummaryEngine
from app.engines.evaluation.session_evaluation_engine import SessionEvaluationEngine


class EvaluationService:
    def __init__(
        self,
        session_repository: SessionRepository,
        evaluation_engine: SessionEvaluationEngine,
        evaluations_summary_engine: EvaluationsSummaryEngine,
        agent_evaluation_repository: AgentEvaluationRepository,
    ) -> None:
        self._session_repository = session_repository
        self._evaluation_engine = evaluation_engine
        self._evaluations_summary_engine = evaluations_summary_engine
        self._agent_evaluation_repository = agent_evaluation_repository

    def evaluate_session(self, session_id: SessionId) -> SessionEvaluation:
        session = self._session_repository.find_by_id(session_id)
        return self._evaluate(session)

    def list_all_evaluations(self) -> tuple[SessionEvaluation, ...]:
        sessions = self._session_repository.list_all()
        return tuple(self._evaluate(session) for session in sessions)

    def evaluations_summary(self) -> EvaluationsSummary:
        agent_evaluations = self._agent_evaluation_repository.list_all()
        if agent_evaluations:
            return self._evaluations_summary_engine.build_summary(agent_evaluations)
        evaluations = self.list_all_evaluations()
        return self._evaluations_summary_engine.build_summary(evaluations)

    def list_agent_evaluations(self) -> tuple[SessionEvaluation, ...]:
        return self._agent_evaluation_repository.list_all()

    def get_agent_session_detail(
        self, session_id: SessionId
    ) -> tuple[SessionEvaluation, ChatSession, str]:
        evaluation = self._agent_evaluation_repository.find_by_session_id(session_id)
        if evaluation is None:
            raise EvaluationNotFoundError(f"Agent evaluation not found for session {session_id.value}")
        chat_session = self._session_repository.find_by_id(session_id)
        session_dict = {
            "id": str(session_id.value),
            "messages": [
                {"role": str(msg.role.value if hasattr(msg.role, "value") else msg.role), "content": msg.content}
                for msg in chat_session.messages
            ],
        }
        prompt_used = build_analysis_prompt(session_dict)
        return evaluation, chat_session, prompt_used

    def _evaluate(self, session: ChatSession) -> SessionEvaluation:
        return self._evaluation_engine.evaluate(session)
