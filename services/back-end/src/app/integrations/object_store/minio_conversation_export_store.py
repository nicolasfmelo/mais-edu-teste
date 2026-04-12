from __future__ import annotations

import io

from minio import Minio
from minio.error import S3Error

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

    def upload_json(self, object_key: str, data: bytes) -> str:
        """Upload raw bytes as an application/json object. Returns the object key."""
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
