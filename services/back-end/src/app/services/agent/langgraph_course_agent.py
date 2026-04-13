from __future__ import annotations

from dataclasses import dataclass, field

from langgraph.graph import END, START, StateGraph

from app.domain_models.agent.models import AgentInvocation, AgentReply
from app.domain_models.common.contracts import AIGatewayClient
from app.domain_models.common.ids import AgentRunId
from app.domain_models.rag.models import RetrievedChunk, RagQuery
from app.engines.agent.prompt_assembly_engine import PromptAssemblyEngine
from app.services.rag.rag_service import RagService


@dataclass(frozen=True)
class CourseAgentGraphState:
    invocation: AgentInvocation
    retrieved_chunks: tuple[RetrievedChunk, ...] = field(default_factory=tuple)
    reply_content: str = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    model_id: str | None = None

    def with_retrieved_chunks(self, retrieved_chunks: tuple[RetrievedChunk, ...]) -> "CourseAgentGraphState":
        return CourseAgentGraphState(
            invocation=self.invocation,
            retrieved_chunks=retrieved_chunks,
            reply_content=self.reply_content,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            model_id=self.model_id,
        )

    def with_reply(
        self,
        reply_content: str,
        prompt_tokens: int | None,
        completion_tokens: int | None,
        model_id: str | None = None,
    ) -> "CourseAgentGraphState":
        return CourseAgentGraphState(
            invocation=self.invocation,
            retrieved_chunks=self.retrieved_chunks,
            reply_content=reply_content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model_id=model_id,
        )

    def with_reply_content(self, reply_content: str) -> "CourseAgentGraphState":
        return self.with_reply(reply_content, self.prompt_tokens, self.completion_tokens, self.model_id)

    def to_payload(self) -> dict[str, object]:
        return {
            "state": self,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> "CourseAgentGraphState":
        state = payload["state"]
        if not isinstance(state, cls):
            raise TypeError("Unexpected agent graph state payload.")
        return state


class LangGraphCourseAgent:
    def __init__(
        self,
        rag_service: RagService,
        ai_gateway_client: AIGatewayClient,
        prompt_assembly_engine: PromptAssemblyEngine,
    ) -> None:
        self._rag_service = rag_service
        self._ai_gateway_client = ai_gateway_client
        self._prompt_assembly_engine = prompt_assembly_engine
        self._graph = self._build_graph()

    def generate_reply(self, invocation: AgentInvocation) -> AgentReply:
        final_payload = self._graph.invoke(CourseAgentGraphState(invocation=invocation).to_payload())
        final_state = CourseAgentGraphState.from_payload(final_payload)
        return AgentReply(
            run_id=AgentRunId.new(),
            content=final_state.reply_content,
            retrieved_chunks=final_state.retrieved_chunks,
            prompt_tokens=final_state.prompt_tokens,
            completion_tokens=final_state.completion_tokens,
            model_id=final_state.model_id,
        )

    def _build_graph(self):
        graph = StateGraph(dict)
        graph.add_node("retrieve_context", self._retrieve_context)
        graph.add_node("invoke_proxy", self._invoke_proxy)
        graph.add_edge(START, "retrieve_context")
        graph.add_edge("retrieve_context", "invoke_proxy")
        graph.add_edge("invoke_proxy", END)
        return graph.compile()

    def _retrieve_context(self, payload: dict[str, object]) -> dict[str, object]:
        state = CourseAgentGraphState.from_payload(payload)
        retrieved_chunks = self._rag_service.retrieve(
            RagQuery(
                session_id=state.invocation.session_id,
                question=state.invocation.latest_user_message,
            )
        )
        return state.with_retrieved_chunks(retrieved_chunks).to_payload()

    def _invoke_proxy(self, payload: dict[str, object]) -> dict[str, object]:
        state = CourseAgentGraphState.from_payload(payload)
        gateway_request = self._prompt_assembly_engine.build_gateway_request(
            invocation=state.invocation,
            retrieved_chunks=state.retrieved_chunks,
        )
        gateway_reply = self._ai_gateway_client.generate_reply(gateway_request)
        return state.with_reply(
            reply_content=gateway_reply.content,
            prompt_tokens=gateway_reply.prompt_tokens,
            completion_tokens=gateway_reply.completion_tokens,
            model_id=gateway_reply.model_id,
        ).to_payload()
