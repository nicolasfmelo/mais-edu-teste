import json
from datetime import datetime, timezone

from app.domain_models.chat.models import ChatMessage, ChatSession, MessageRole
from app.domain_models.common.ids import MessageId, SessionId
from app.engines.chat.conversation_export_engine import build_export_payload
from app.integrations.object_store.minio_conversation_export_store import _serialize_export_payload


def test_serialize_export_payload_produces_expected_json_shape() -> None:
    exported_at = datetime(2026, 1, 2, 10, 30, tzinfo=timezone.utc)
    session = ChatSession(
        id=SessionId.new(),
        messages=(
            ChatMessage(
                id=MessageId.new(),
                role=MessageRole.USER,
                content="Mensagem de teste",
                created_at=exported_at,
            ),
        ),
        status="active",
        created_at=exported_at,
        updated_at=exported_at,
        last_message_at=exported_at,
    )
    payload = build_export_payload((session,), exported_at=exported_at)

    raw = _serialize_export_payload(payload)
    parsed = json.loads(raw.decode("utf-8"))

    assert parsed["exported_at"] == exported_at.isoformat()
    assert parsed["session_count"] == 1
    assert parsed["sessions"][0]["id"] == str(session.id.value)
    assert parsed["sessions"][0]["messages"][0]["role"] == "user"
    assert parsed["sessions"][0]["messages"][0]["content"] == "Mensagem de teste"
