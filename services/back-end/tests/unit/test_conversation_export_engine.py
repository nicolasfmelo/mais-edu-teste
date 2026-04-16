from datetime import datetime, timezone

from app.domain_models.chat.models import ChatMessage, ChatSession, MessageRole
from app.domain_models.common.ids import MessageId, SessionId
from app.engines.chat.conversation_export_engine import build_export_payload


def test_build_export_payload_maps_chat_sessions_to_domain_payload() -> None:
    created_at = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    session_id = SessionId.new()
    message_id = MessageId.new()
    session = ChatSession(
        id=session_id,
        status="active",
        created_at=created_at,
        updated_at=created_at,
        last_message_at=created_at,
        messages=(
            ChatMessage(
                id=message_id,
                role=MessageRole.USER,
                content="Quero mais detalhes",
                created_at=created_at,
            ),
        ),
    )

    payload = build_export_payload((session,), exported_at=created_at)

    assert payload.exported_at == created_at
    assert payload.session_count == 1
    assert payload.sessions[0].id == session_id
    assert payload.sessions[0].messages[0].id == message_id
    assert payload.sessions[0].messages[0].role == MessageRole.USER
    assert payload.sessions[0].messages[0].content == "Quero mais detalhes"
