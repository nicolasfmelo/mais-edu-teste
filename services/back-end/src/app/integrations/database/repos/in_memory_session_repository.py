from __future__ import annotations

from app.domain_models.chat.models import ChatSession
from app.domain_models.common.exceptions import SessionNotFoundError
from app.domain_models.common.ids import SessionId


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, ChatSession] = {}

    def get_or_create(self, session_id: SessionId) -> ChatSession:
        return self._sessions.setdefault(str(session_id), ChatSession(id=session_id))

    def save(self, session: ChatSession) -> ChatSession:
        self._sessions[str(session.id)] = session
        return session

    def find_by_id(self, session_id: SessionId) -> ChatSession:
        session = self._sessions.get(str(session_id))
        if session is None:
            raise SessionNotFoundError(f"Session {session_id} not found")
        return session
