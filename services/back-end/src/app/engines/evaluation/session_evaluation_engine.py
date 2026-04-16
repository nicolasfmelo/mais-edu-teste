from __future__ import annotations

from app.domain_models.chat.models import ChatSession, MessageRole
from app.domain_models.evaluation.models import EvaluationEvidence, SatisfactionClass, SessionEvaluation


class SessionEvaluationEngine:
    """Pure heuristics for the first evaluation scaffold."""

    def evaluate(self, session: ChatSession) -> SessionEvaluation:
        user_messages = tuple(message for message in session.messages if message.role == MessageRole.USER)
        assistant_messages = tuple(message for message in session.messages if message.role == MessageRole.ASSISTANT)
        all_content = " ".join(message.content.lower() for message in session.messages)

        satisfaction = SatisfactionClass.GOOD if "obrigad" in all_content else SatisfactionClass.NEUTRAL
        if "não" in all_content and "entendeu" in all_content:
            satisfaction = SatisfactionClass.BAD

        evidences = tuple(EvaluationEvidence(snippet=message.content[:140]) for message in user_messages[:2])
        if satisfaction == SatisfactionClass.GOOD:
            resolution_score = 2
        elif assistant_messages:
            resolution_score = 1
        else:
            resolution_score = 0

        return SessionEvaluation(
            session_id=session.id,
            satisfaction=satisfaction,
            effort_score=1 if len(user_messages) <= 2 else 3,
            understanding_score=2 if assistant_messages else 0,
            resolution_score=resolution_score,
            evidences=evidences,
        )
