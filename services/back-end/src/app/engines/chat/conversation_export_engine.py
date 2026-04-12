from __future__ import annotations

import json
from datetime import datetime, timezone

from app.domain_models.chat.models import ChatSession


def serialize_sessions_to_json(sessions: tuple[ChatSession, ...]) -> bytes:
    """Pure function — serializes chat sessions to UTF-8 JSON bytes.

    Each session includes its id, status, timestamps and an ordered list of messages.
    """
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "session_count": len(sessions),
        "sessions": [_session_to_dict(s) for s in sessions],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def _session_to_dict(session: ChatSession) -> dict:
    return {
        "id": str(session.id.value),
        "status": session.status,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        "last_message_at": session.last_message_at.isoformat() if session.last_message_at else None,
        "messages": [
            {
                "id": str(msg.id.value),
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in session.messages
        ],
    }
