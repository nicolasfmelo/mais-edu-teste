from __future__ import annotations

from app.domain_models.agent.models import AgentInvocation, AgentReply
from app.domain_models.chat.models import ChatSession
from app.services.agent.langgraph_course_agent import LangGraphCourseAgent


class AgentService:
    def __init__(
        self,
        course_agent: LangGraphCourseAgent,
    ) -> None:
        self._course_agent = course_agent

    def generate_reply(self, session: ChatSession, invocation: AgentInvocation) -> AgentReply:
        return self._course_agent.generate_reply(
            AgentInvocation(
                session_id=session.id,
                api_key=invocation.api_key,
                idempotency_key=invocation.idempotency_key,
                latest_user_message=invocation.latest_user_message,
                conversation_messages=session.messages,
                model_id=invocation.model_id,
                system_prompt=invocation.system_prompt,
            )
        )
