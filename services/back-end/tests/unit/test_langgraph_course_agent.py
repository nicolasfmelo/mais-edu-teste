from app.domain_models.agent.models import AgentInvocation, GatewayPromptReply, GatewayPromptRequest
from app.domain_models.chat.models import ChatMessage, MessageRole
from app.domain_models.common.ids import DocumentId, MessageId, SessionId
from app.domain_models.rag.models import RetrievedChunk
from app.engines.agent.prompt_assembly_engine import PromptAssemblyEngine
from app.services.agent.langgraph_course_agent import LangGraphCourseAgent


class StubRagService:
    def retrieve(self, query):  # noqa: ANN001
        assert query.question == "Quero um curso de dados."
        return (
            RetrievedChunk(
                document_id=DocumentId.new(),
                content="Pos-graduacao em Ciencia de Dados com foco em analytics.",
                score=0.95,
            ),
        )


class StubAIGatewayClient:
    def __init__(self) -> None:
        self.request: GatewayPromptRequest | None = None

    def generate_reply(self, request: GatewayPromptRequest) -> GatewayPromptReply:
        self.request = request
        return GatewayPromptReply(content="Resposta do proxy", model_id=request.model_id)


def test_langgraph_course_agent_uses_state_class_and_returns_reply() -> None:
    gateway_client = StubAIGatewayClient()
    agent = LangGraphCourseAgent(
        rag_service=StubRagService(),
        ai_gateway_client=gateway_client,
        prompt_assembly_engine=PromptAssemblyEngine(),
    )

    reply = agent.generate_reply(
        AgentInvocation(
            session_id=SessionId.new(),
            api_key="key_123",
            idempotency_key="chat-1",
            latest_user_message="Quero um curso de dados.",
            conversation_messages=(
                ChatMessage(id=MessageId.new(), role=MessageRole.USER, content="Quero um curso de dados."),
            ),
            model_id="us.amazon.nova-2-lite-v1:0",
            system_prompt="Ajude o aluno a escolher um curso.",
        )
    )

    assert reply.content == "Resposta do proxy"
    assert len(reply.retrieved_chunks) == 1
    assert gateway_client.request is not None
    assert gateway_client.request.api_key == "key_123"
    assert "Ciencia de Dados" in gateway_client.request.prompt
