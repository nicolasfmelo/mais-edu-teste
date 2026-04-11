from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.domain_models.chat.models import ChatMessage, ChatSession, MessageRole
from app.domain_models.common.exceptions import SessionNotFoundError, StorageUnavailableError
from app.domain_models.common.ids import MessageId, SessionId
from app.integrations.database.models.chat_models import ChatMessageModel, ChatSessionModel
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemySessionRepository:
    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def get_or_create(self, session_id: SessionId) -> ChatSession:
        try:
            with self._database.session_scope() as session:
                model = session.get(
                    ChatSessionModel,
                    session_id.value,
                    options=(selectinload(ChatSessionModel.messages),),
                )
                if model is None:
                    return ChatSession(id=session_id)
                return self._to_domain(model)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to load chat session.") from exc

    def save(self, session_data: ChatSession) -> ChatSession:
        try:
            with self._database.session_scope() as session:
                model = session.get(
                    ChatSessionModel,
                    session_data.id.value,
                    options=(selectinload(ChatSessionModel.messages),),
                )
                if model is None:
                    model = ChatSessionModel(
                        id=session_data.id.value,
                        status="active",
                    )
                    session.add(model)
                    session.flush()

                model.last_message_at = datetime.now(timezone.utc) if session_data.messages else None
                session.execute(delete(ChatMessageModel).where(ChatMessageModel.session_id == session_data.id.value))
                model.messages = []
                for index, message in enumerate(session_data.messages, start=1):
                    model.messages.append(
                        ChatMessageModel(
                            id=message.id.value,
                            session_id=session_data.id.value,
                            sequence_number=index,
                            role=message.role.value,
                            content=message.content,
                        )
                    )
                session.flush()
                session.refresh(model)
                return self._to_domain(model)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to save chat session.") from exc

    def find_by_id(self, session_id: SessionId) -> ChatSession:
        try:
            with self._database.session_scope() as session:
                model = session.get(
                    ChatSessionModel,
                    session_id.value,
                    options=(selectinload(ChatSessionModel.messages),),
                )
                if model is None:
                    raise SessionNotFoundError(f"Session {session_id} not found")
                return self._to_domain(model)
        except SessionNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to find chat session.") from exc

    def _to_domain(self, model: ChatSessionModel) -> ChatSession:
        ordered_messages = sorted(model.messages, key=lambda item: item.sequence_number)
        return ChatSession(
            id=SessionId(value=model.id),
            messages=tuple(
                ChatMessage(
                    id=MessageId(value=message.id),
                    role=MessageRole(message.role),
                    content=message.content,
                )
                for message in ordered_messages
            ),
        )
