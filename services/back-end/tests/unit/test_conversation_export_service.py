from datetime import datetime, timezone

from app.domain_models.chat.models import ChatMessage, ChatSession, MessageRole
from app.domain_models.common.ids import MessageId, SessionId
from app.domain_models.metrics.job_models import MetricsJob, MetricsJobStatus, MetricsJobType
from app.services.chat.conversation_export_service import ConversationExportService


class _StubSessionRepository:
    def __init__(self, sessions: tuple[ChatSession, ...]) -> None:
        self._sessions = sessions

    def get_or_create(self, session_id: SessionId) -> ChatSession:  # pragma: no cover - not used here
        raise NotImplementedError

    def save(self, session: ChatSession) -> ChatSession:  # pragma: no cover - not used here
        raise NotImplementedError

    def find_by_id(self, session_id: SessionId) -> ChatSession:  # pragma: no cover - not used here
        raise NotImplementedError

    def list_all(self) -> tuple[ChatSession, ...]:
        return self._sessions


class _StubExportStore:
    def __init__(self) -> None:
        self.last_object_key: str | None = None
        self.last_payload = None

    def upload_payload(self, object_key: str, payload):  # noqa: ANN001
        self.last_object_key = object_key
        self.last_payload = payload
        return object_key


class _StubMetricsJobRepository:
    def __init__(self) -> None:
        self.updates: list[tuple[int, MetricsJobStatus, dict[str, object]]] = []

    def create_job(self, job_type: MetricsJobType) -> MetricsJob:
        return MetricsJob(
            id=1,
            job_type=job_type,
            status=MetricsJobStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )

    def update_job(self, job_id: int, status: MetricsJobStatus, **kwargs: object) -> MetricsJob:
        self.updates.append((job_id, status, kwargs))
        return MetricsJob(
            id=job_id,
            job_type=MetricsJobType.EXPORT,
            status=status,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            session_count=kwargs.get("session_count") if isinstance(kwargs.get("session_count"), int) else None,
            object_key=kwargs.get("object_key") if isinstance(kwargs.get("object_key"), str) else None,
            error_message=kwargs.get("error_message") if isinstance(kwargs.get("error_message"), str) else None,
        )

    def get_latest_job(self, job_type: MetricsJobType) -> MetricsJob | None:  # pragma: no cover - not used here
        return None


def test_conversation_export_service_builds_payload_and_updates_job() -> None:
    message = ChatMessage(
        id=MessageId.new(),
        role=MessageRole.USER,
        content="Quero informações",
    )
    session = ChatSession(id=SessionId.new(), messages=(message,))
    session_repo = _StubSessionRepository((session,))
    export_store = _StubExportStore()
    job_repo = _StubMetricsJobRepository()
    service = ConversationExportService(
        session_repository=session_repo,
        export_store=export_store,
        metrics_job_repository=job_repo,
    )

    result = service.export_all()

    assert result.session_count == 1
    assert result.object_key.startswith("conversations/export_")
    assert export_store.last_object_key == result.object_key
    assert export_store.last_payload is not None
    assert export_store.last_payload.session_count == 1
    assert len(job_repo.updates) == 1
    assert job_repo.updates[0][1] == MetricsJobStatus.DONE
