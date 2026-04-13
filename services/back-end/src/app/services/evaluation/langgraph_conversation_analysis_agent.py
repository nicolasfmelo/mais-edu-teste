from __future__ import annotations

from dataclasses import dataclass, field

from langgraph.graph import END, START, StateGraph

from app.domain_models.agent.models import GatewayPromptRequest
from app.domain_models.common.contracts import AIGatewayClient, ConversationSessionSource
from app.domain_models.common.exceptions import ConversationAnalysisError
from app.domain_models.evaluation.models import ExportedConversationSession, SessionEvaluation
from app.engines.evaluation.conversation_analysis_parser_engine import parse_session_evaluation
from app.engines.evaluation.conversation_analysis_prompt_engine import build_analysis_prompt, parse_analysis_response
from app.engines.evaluation.prompt_injection_detector_engine import detect_injection
from app.integrations.langgraph.state_payload_adapter import LangGraphStatePayloadAdapter
from app.services.prompt.agent_prompt_service import AgentPromptService


@dataclass(frozen=True)
class ConversationAnalysisGraphState:
    api_key: str
    model_id: str | None
    sessions: tuple[ExportedConversationSession, ...] = field(default_factory=tuple)
    evaluations: tuple[SessionEvaluation, ...] = field(default_factory=tuple)

    def with_sessions(self, sessions: tuple[ExportedConversationSession, ...]) -> "ConversationAnalysisGraphState":
        return ConversationAnalysisGraphState(
            api_key=self.api_key,
            model_id=self.model_id,
            sessions=sessions,
            evaluations=self.evaluations,
        )

    def with_evaluations(self, evaluations: tuple[SessionEvaluation, ...]) -> "ConversationAnalysisGraphState":
        return ConversationAnalysisGraphState(
            api_key=self.api_key,
            model_id=self.model_id,
            sessions=self.sessions,
            evaluations=evaluations,
        )

class LangGraphConversationAnalysisAgent:
    def __init__(
        self,
        conversation_reader: ConversationSessionSource,
        ai_gateway_client: AIGatewayClient,
        agent_prompt_service: AgentPromptService,
    ) -> None:
        self._conversation_reader = conversation_reader
        self._ai_gateway_client = ai_gateway_client
        self._agent_prompt_service = agent_prompt_service
        self._payload_adapter = LangGraphStatePayloadAdapter(
            ConversationAnalysisGraphState,
            "conversation analysis graph state",
        )
        self._graph = self._build_graph()

    def analyze(self, api_key: str, model_id: str | None = None) -> tuple[SessionEvaluation, ...]:
        initial = ConversationAnalysisGraphState(api_key=api_key, model_id=model_id)
        final_payload = self._graph.invoke(self._payload_adapter.to_payload(initial))
        return self._payload_adapter.from_payload(final_payload).evaluations

    def _build_graph(self):
        graph = StateGraph(dict)
        graph.add_node("load_sessions", self._payload_adapter.wrap_node(self._load_sessions))
        graph.add_node("analyze_sessions", self._payload_adapter.wrap_node(self._analyze_sessions))
        graph.add_edge(START, "load_sessions")
        graph.add_edge("load_sessions", "analyze_sessions")
        graph.add_edge("analyze_sessions", END)
        return graph.compile()

    def _load_sessions(self, state: ConversationAnalysisGraphState) -> ConversationAnalysisGraphState:
        sessions = self._conversation_reader.list_sessions()
        return state.with_sessions(sessions)

    def _analyze_sessions(self, state: ConversationAnalysisGraphState) -> ConversationAnalysisGraphState:
        evaluations = tuple(self._analyze_one(session, state.api_key, state.model_id) for session in state.sessions)
        return state.with_evaluations(evaluations)

    def _analyze_one(
        self,
        session: ExportedConversationSession,
        api_key: str,
        model_id: str | None,
    ) -> SessionEvaluation:
        heuristic_detected, heuristic_snippets = detect_injection(session.messages)
        prompt = build_analysis_prompt(session, self._agent_prompt_service.get_nps_system_prompt())
        request = GatewayPromptRequest(
            api_key=api_key,
            idempotency_key=f"analysis-{session.session_id}",
            prompt=prompt,
            model_id=model_id,
        )
        try:
            reply = self._ai_gateway_client.generate_reply(request)
            parsed = parse_analysis_response(reply.content)
            return parse_session_evaluation(
                session_id=session.session_id,
                parsed=parsed,
                prompt_tokens=reply.prompt_tokens,
                completion_tokens=reply.completion_tokens,
                heuristic_injection_detected=heuristic_detected,
                heuristic_injection_snippets=heuristic_snippets,
            )
        except Exception as exc:
            raise ConversationAnalysisError(f"Analysis failed for session '{session.session_id}': {exc}") from exc
