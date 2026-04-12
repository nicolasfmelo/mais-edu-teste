from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from app.domain_models.chat.export_models import ConversationExportResult
from app.domain_models.common.contracts import MetricsJobRepository
from app.domain_models.metrics.job_models import MetricsJobStatus, MetricsJobType
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
        metrics_job_repository: MetricsJobRepository,
    ) -> None:
        self._session_repository = session_repository
        self._export_store = export_store
        self._metrics_job_repository = metrics_job_repository

    def export_all(self) -> ConversationExportResult:
        job = self._metrics_job_repository.create_job(MetricsJobType.EXPORT)
        try:
            sessions = self._session_repository.list_all()
            exported_at = datetime.now(timezone.utc)
            data = serialize_sessions_to_json(sessions)
            object_key = f"conversations/export_{exported_at.strftime('%Y%m%dT%H%M%S')}.json"
            self._export_store.upload_json(object_key, data)
            self._metrics_job_repository.update_job(
                job.id,
                MetricsJobStatus.DONE,
                session_count=len(sessions),
                object_key=object_key,
            )
            return ConversationExportResult(
                object_key=object_key,
                session_count=len(sessions),
                exported_at=exported_at,
            )
        except Exception as exc:
            self._metrics_job_repository.update_job(job.id, MetricsJobStatus.ERROR, error_message=str(exc))
            raise
