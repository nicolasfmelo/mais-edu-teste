from app.domain_models.agent.models import AgentInvocation, InstitutionProfile
from app.domain_models.chat.models import ChatMessage, MessageRole
from app.domain_models.common.ids import DocumentId, MessageId, SessionId
from app.domain_models.rag.models import RetrievedChunk
from app.engines.agent.prompt_assembly_engine import PromptAssemblyEngine


def test_prompt_assembly_engine_builds_gateway_prompt_with_system_history_and_context() -> None:
    engine = PromptAssemblyEngine(
        institution_profile=InstitutionProfile(
            institution_name="Instituto Horizonte Digital",
            agent_name="Clara",
            presentation_example="Oi, eu sou a Clara, assistente virtual do Instituto Horizonte Digital.",
            briefing_markdown="Perfil institucional resumido.",
        )
    )
    invocation = AgentInvocation(
        session_id=SessionId.new(),
        api_key="key_123",
        idempotency_key="chat-op-1",
        latest_user_message="Quero um MBA remoto em lideranca.",
        conversation_messages=(
            ChatMessage(id=MessageId.new(), role=MessageRole.USER, content="Quero migrar para gestao."),
            ChatMessage(id=MessageId.new(), role=MessageRole.ASSISTANT, content="Posso te ajudar com isso."),
        ),
        model_id="us.anthropic.claude-sonnet-4-6",
        system_prompt="Atue como consultora educacional.",
    )

    gateway_request = engine.build_gateway_request(
        invocation=invocation,
        retrieved_chunks=(
            RetrievedChunk(
                document_id=DocumentId.new(),
                content="MBA em Lideranca e Gestao de Pessoas na modalidade Remoto.",
                score=0.9,
            ),
        ),
    )

    assert gateway_request.api_key == "key_123"
    assert gateway_request.idempotency_key == "chat-op-1"
    assert gateway_request.model_id == "us.anthropic.claude-sonnet-4-6"
    assert "SISTEMA" in gateway_request.prompt
    assert "PERFIL INSTITUCIONAL E DA AGENTE" in gateway_request.prompt
    assert "HISTORICO DA CONVERSA" in gateway_request.prompt
    assert "CONTEXTO RECUPERADO" in gateway_request.prompt
    assert "PERGUNTA ATUAL DO USUARIO" in gateway_request.prompt


def test_prompt_assembly_engine_adds_opening_instruction_on_first_turn() -> None:
    engine = PromptAssemblyEngine(
        institution_profile=InstitutionProfile(
            institution_name="Instituto Horizonte Digital",
            agent_name="Clara",
            presentation_example="Oi, eu sou a Clara, assistente virtual do Instituto Horizonte Digital.",
            briefing_markdown="Perfil institucional resumido.",
        )
    )
    invocation = AgentInvocation(
        session_id=SessionId.new(),
        api_key="key_123",
        idempotency_key="chat-op-1",
        latest_user_message="Quero um curso de dados.",
        conversation_messages=(
            ChatMessage(id=MessageId.new(), role=MessageRole.USER, content="Quero um curso de dados."),
        ),
    )

    gateway_request = engine.build_gateway_request(invocation=invocation, retrieved_chunks=())

    assert "INSTRUCAO DE ABERTURA" in gateway_request.prompt
    assert "Clara" in gateway_request.prompt
