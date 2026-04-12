from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from app.domain_models.chat.export_models import ConversationExportResult
from app.engines.chat.conversation_export_engine import serialize_sessions_to_json


class SessionRepositoryProtocol(Protocol):
    def list_all(self) -> tuple: ...


class ConversationExportStoreProtocol(Protocol):
    def upload_json(self, object_key: str, data: bytes) -> str: ...


class ConversationExportService:
    def __init__(
        self,
        session_repository: SessionRepositoryProtocol,
        export_store: ConversationExportStoreProtocol,
    ) -> None:
        self._session_repository = session_repository
        self._export_store = export_store

    def export_all(self) -> ConversationExportResult:
        sessions = self._session_repository.list_all()
        exported_at = datetime.now(timezone.utc)
        data = serialize_sessions_to_json(sessions)
        object_key = f"conversations/export_{exported_at.strftime('%Y%m%dT%H%M%S')}.json"
        self._export_store.upload_json(object_key, data)
        return ConversationExportResult(
            object_key=object_key,
            session_count=len(sessions),
            exported_at=exported_at,
        )
