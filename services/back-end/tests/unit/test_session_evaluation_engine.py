from app.domain_models.chat.models import ChatMessage, ChatSession, MessageRole
from app.domain_models.common.ids import MessageId, SessionId
from app.engines.evaluation.session_evaluation_engine import SessionEvaluationEngine


def test_session_evaluation_marks_grateful_flow_as_good() -> None:
    engine = SessionEvaluationEngine()
    session = ChatSession(
        id=SessionId.new(),
        messages=(
            ChatMessage(id=MessageId.new(), role=MessageRole.USER, content="Quero saber sobre pedagogia"),
            ChatMessage(id=MessageId.new(), role=MessageRole.ASSISTANT, content="Posso ajudar com isso"),
            ChatMessage(id=MessageId.new(), role=MessageRole.USER, content="Obrigado, era isso"),
        ),
    )

    evaluation = engine.evaluate(session)

    assert evaluation.satisfaction.value == "bom"
    assert evaluation.understanding_score == 2
