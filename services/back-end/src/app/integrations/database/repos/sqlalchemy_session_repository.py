from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain_models.chat.models import ChatMessage, ChatSession, MessageRole
from app.domain_models.common.exceptions import SessionNotFoundError
from app.domain_models.common.ids import MessageId, SessionId
from app.integrations.database.models.chat_models import ChatMessageModel, ChatSessionModel
from app.integrations.database.repos._sqlalchemy_utils import (
    EntityLookup,
    load_entity,
    require_entity,
    with_storage_error,
)
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemySessionRepository:
    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def get_or_create(self, session_id: SessionId) -> ChatSession:
        return with_storage_error(
            lambda: self._get_or_create(session_id),
            message="Unable to load chat session.",
        )

    def save(self, session_data: ChatSession) -> ChatSession:
        return with_storage_error(
            lambda: self._save(session_data),
            message="Unable to save chat session.",
        )

    def find_by_id(self, session_id: SessionId) -> ChatSession:
        return with_storage_error(
            lambda: self._find_by_id(session_id),
            message="Unable to find chat session.",
        )

    def list_all(self) -> tuple[ChatSession, ...]:
        return with_storage_error(
            self._list_all,
            message="Unable to list chat sessions.",
        )

    def _get_or_create(self, session_id: SessionId) -> ChatSession:
        with self._database.session_scope() as session:
            model = load_entity(session, self._session_lookup(session_id))
            if model is None:
                return ChatSession(id=session_id)
            return self._to_domain(model)

    def _save(self, session_data: ChatSession) -> ChatSession:
        with self._database.session_scope() as session:
            model = load_entity(session, self._session_lookup(session_data.id))
            if model is None:
                model = ChatSessionModel(
                    id=session_data.id.value,
                    status="active",
                )
                session.add(model)
                session.flush()

            model.status = session_data.status
            model.last_message_at = datetime.now(timezone.utc) if session_data.messages else None
            existing_messages = {message.id: message for message in model.messages}
            ordered_messages: list[ChatMessageModel] = []
            for index, message in enumerate(session_data.messages, start=1):
                persisted_message = existing_messages.pop(message.id.value, None)
                if persisted_message is None:
                    persisted_message = ChatMessageModel(
                        id=message.id.value,
                        session_id=session_data.id.value,
                        sequence_number=index,
                        role=message.role.value,
                        content=message.content,
                    )
                else:
                    persisted_message.sequence_number = index
                    persisted_message.role = message.role.value
                    persisted_message.content = message.content
                ordered_messages.append(persisted_message)

            for stale_message in existing_messages.values():
                session.delete(stale_message)

            model.messages = ordered_messages
            session.flush()
            session.refresh(model)
            return self._to_domain(model)

    def _find_by_id(self, session_id: SessionId) -> ChatSession:
        with self._database.session_scope() as session:
            model = require_entity(session, self._required_session_lookup(session_id))
            return self._to_domain(model)

    def _list_all(self) -> tuple[ChatSession, ...]:
        with self._database.session_scope() as session:
            models = session.execute(
                select(ChatSessionModel)
                .options(selectinload(ChatSessionModel.messages))
                .order_by(
                    ChatSessionModel.last_message_at.is_(None),
                    ChatSessionModel.last_message_at.desc(),
                    ChatSessionModel.created_at.desc(),
                )
            ).scalars()
            return tuple(self._to_domain(model) for model in models)

    def _session_lookup(self, session_id: SessionId) -> EntityLookup[ChatSessionModel, SessionNotFoundError]:
        return EntityLookup(
            model_type=ChatSessionModel,
            entity_id=session_id.value,
            options=(selectinload(ChatSessionModel.messages),),
        )

    def _required_session_lookup(
        self,
        session_id: SessionId,
    ) -> EntityLookup[ChatSessionModel, SessionNotFoundError]:
        return EntityLookup(
            model_type=ChatSessionModel,
            entity_id=session_id.value,
            options=(selectinload(ChatSessionModel.messages),),
            not_found=lambda: SessionNotFoundError(f"Session {session_id} not found"),
        )

    def _to_domain(self, model: ChatSessionModel) -> ChatSession:
        ordered_messages = sorted(model.messages, key=lambda item: item.sequence_number)
        return ChatSession(
            id=SessionId(value=model.id),
            messages=tuple(
                ChatMessage(
                    id=MessageId(value=message.id),
                    role=MessageRole(message.role),
                    content=message.content,
                    created_at=message.created_at,
                )
                for message in ordered_messages
            ),
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_message_at=model.last_message_at,
        )
