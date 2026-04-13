import json
from uuid import uuid4

import pytest

from app.domain_models.common.exceptions import ConversationAnalysisError
from app.integrations.object_store.minio_conversation_reader import MinioConversationReader


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def close(self) -> None:
        return None

    def release_conn(self) -> None:
        return None


class _FakeObject:
    def __init__(self, object_name: str) -> None:
        self.object_name = object_name


class _FakeMinioClient:
    def __init__(self, payloads: dict[str, dict[str, object]]) -> None:
        self._payloads = payloads

    def list_objects(self, bucket: str, prefix: str, recursive: bool):  # noqa: ANN001
        return [_FakeObject(object_name) for object_name in self._payloads]

    def get_object(self, bucket: str, object_name: str) -> _FakeResponse:
        return _FakeResponse(self._payloads[object_name])


def test_minio_conversation_reader_returns_typed_sessions() -> None:
    session_id = str(uuid4())
    reader = MinioConversationReader(
        endpoint="localhost:9000",
        access_key="access",
        secret_key="secret",
        bucket="bucket",
    )
    reader._client = _FakeMinioClient(  # type: ignore[attr-defined]
        {
            "conversations/export.json": {
                "sessions": [
                    {
                        "id": session_id,
                        "messages": [
                            {"role": "user", "content": "Quero detalhes do curso"},
                            {"role": "assistant", "content": "Vou te ajudar"},
                        ],
                    }
                ]
            }
        }
    )

    sessions = reader.list_sessions()

    assert len(sessions) == 1
    assert str(sessions[0].session_id) == session_id
    assert sessions[0].messages[0].role == "user"
    assert sessions[0].messages[0].content == "Quero detalhes do curso"


def test_minio_conversation_reader_rejects_invalid_session_payload() -> None:
    reader = MinioConversationReader(
        endpoint="localhost:9000",
        access_key="access",
        secret_key="secret",
        bucket="bucket",
    )
    reader._client = _FakeMinioClient(  # type: ignore[attr-defined]
        {"conversations/export.json": {"sessions": [{"id": "invalid-uuid", "messages": []}]}}
    )

    with pytest.raises(ConversationAnalysisError):
        reader.list_sessions()
