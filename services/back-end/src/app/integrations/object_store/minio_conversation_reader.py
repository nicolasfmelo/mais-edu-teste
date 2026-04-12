from __future__ import annotations

import io
import json

from minio import Minio
from minio.error import S3Error

from app.domain_models.common.exceptions import ConversationAnalysisError

_CONVERSATIONS_PREFIX = "conversations/"


class MinioConversationReader:
    """Reads exported conversation JSON files from a MinIO bucket.

    Each object under the 'conversations/' prefix is expected to be a JSON export
    produced by serialize_sessions_to_json(), containing a top-level 'sessions' list.
    """

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

    def list_sessions(self) -> list[dict]:
        """Downloads all conversation export objects and returns a flat list of session dicts."""
        try:
            objects = list(self._client.list_objects(self._bucket, prefix=_CONVERSATIONS_PREFIX, recursive=True))
        except S3Error as exc:
            raise ConversationAnalysisError(f"Cannot list objects in bucket '{self._bucket}': {exc}") from exc

        sessions_by_id: dict[str, dict] = {}
        unkeyed: list[dict] = []
        for obj in objects:
            for session in self._load_sessions_from_object(obj.object_name):
                session_id = session.get("id")
                if session_id:
                    sessions_by_id[str(session_id)] = session  # latest export wins
                else:
                    unkeyed.append(session)
        return list(sessions_by_id.values()) + unkeyed

    def _load_sessions_from_object(self, object_name: str) -> list[dict]:
        response = None
        try:
            response = self._client.get_object(self._bucket, object_name)
            raw = response.read()
        except S3Error as exc:
            raise ConversationAnalysisError(f"Cannot read object '{object_name}': {exc}") from exc
        finally:
            if response:
                response.close()
                response.release_conn()

        try:
            payload = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ConversationAnalysisError(f"Invalid JSON in object '{object_name}': {exc}") from exc

        return payload.get("sessions", [])
