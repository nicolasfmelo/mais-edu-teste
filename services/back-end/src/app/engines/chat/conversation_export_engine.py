from __future__ import annotations

from datetime import datetime, timezone

from app.domain_models.chat.export_models import ConversationExportPayload, ConversationExportSession
from app.domain_models.chat.models import ChatSession


def build_export_payload(
    sessions: tuple[ChatSession, ...],
    *,
    exported_at: datetime | None = None,
) -> ConversationExportPayload:
    """Pure function — maps chat sessions to an export payload domain model."""
    return ConversationExportPayload(
        exported_at=exported_at or datetime.now(timezone.utc),
        sessions=tuple(ConversationExportSession.from_chat_session(session) for session in sessions),
    )
