from pathlib import Path

from app.domain_models.chat.models import ChatMessage, ChatSession, MessageRole
from app.domain_models.common.ids import MessageId, SessionId
from app.integrations.database.repos.sqlalchemy_session_repository import SQLAlchemySessionRepository
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


def test_sqlalchemy_session_repository_persists_and_reads_session(tmp_path: Path) -> None:
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'session.db'}")
    database.create_schema()
    repository = SQLAlchemySessionRepository(database)

    session_id = SessionId.new()
    saved = repository.save(
        ChatSession(
            id=session_id,
            messages=(
                ChatMessage(id=MessageId.new(), role=MessageRole.USER, content="Oi"),
                ChatMessage(id=MessageId.new(), role=MessageRole.ASSISTANT, content="Ola"),
            ),
        )
    )

    loaded = repository.find_by_id(session_id)

    assert saved.id == session_id
    assert len(loaded.messages) == 2
    assert loaded.messages[0].role == MessageRole.USER
    assert loaded.messages[1].content == "Ola"


def test_sqlalchemy_session_repository_preserves_existing_message_timestamps(tmp_path: Path) -> None:
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'session-preserve.db'}")
    database.create_schema()
    repository = SQLAlchemySessionRepository(database)

    first_message = ChatMessage(id=MessageId.new(), role=MessageRole.USER, content="Oi")
    session_id = SessionId.new()
    initial_save = repository.save(ChatSession(id=session_id, messages=(first_message,)))

    updated_save = repository.save(
        ChatSession(
            id=session_id,
            messages=(
                initial_save.messages[0],
                ChatMessage(id=MessageId.new(), role=MessageRole.ASSISTANT, content="Ola"),
            ),
        )
    )

    assert initial_save.messages[0].created_at is not None
    assert updated_save.messages[0].created_at == initial_save.messages[0].created_at
