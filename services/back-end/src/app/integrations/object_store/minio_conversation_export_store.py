from __future__ import annotations

import io
import json

from minio import Minio
from minio.error import S3Error

from app.domain_models.chat.export_models import ConversationExportPayload
from app.domain_models.common.exceptions import ConversationExportError


class MinioConversationExportStore:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
    ) -> None:
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
        self._bucket = bucket

    def ensure_bucket(self) -> None:
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
        except S3Error as exc:
            raise ConversationExportError(f"Cannot access MinIO bucket '{self._bucket}': {exc}") from exc

    def upload_payload(self, object_key: str, payload: ConversationExportPayload) -> str:
        """Upload an export payload as a JSON object. Returns the object key."""
        data = _serialize_export_payload(payload)
        try:
            self.ensure_bucket()
            self._client.put_object(
                bucket_name=self._bucket,
                object_name=object_key,
                data=io.BytesIO(data),
                length=len(data),
                content_type="application/json",
            )
            return object_key
        except S3Error as exc:
            raise ConversationExportError(f"Failed to upload export to MinIO: {exc}") from exc


def _serialize_export_payload(payload: ConversationExportPayload) -> bytes:
    serialized_payload = {
        "exported_at": payload.exported_at.isoformat(),
        "session_count": payload.session_count,
        "sessions": [
            {
                "id": str(session.id.value),
                "status": session.status,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                "last_message_at": session.last_message_at.isoformat() if session.last_message_at else None,
                "messages": [
                    {
                        "id": str(message.id.value),
                        "role": message.role.value,
                        "content": message.content,
                        "created_at": message.created_at.isoformat() if message.created_at else None,
                    }
                    for message in session.messages
                ],
            }
            for session in payload.sessions
        ],
    }
    return json.dumps(serialized_payload, ensure_ascii=False, indent=2).encode("utf-8")
