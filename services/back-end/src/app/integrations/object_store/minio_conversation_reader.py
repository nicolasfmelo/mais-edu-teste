from __future__ import annotations

import json
from uuid import UUID

from minio import Minio
from minio.error import S3Error

from app.domain_models.common.exceptions import ConversationAnalysisError
from app.domain_models.common.ids import SessionId
from app.domain_models.evaluation.models import ExportedConversationMessage, ExportedConversationSession

_CONVERSATIONS_PREFIX = "conversations/"


class MinioConversationReader:
    """Reads exported conversation JSON files from a MinIO bucket.

    Each object under the 'conversations/' prefix is expected to be a JSON export
    produced from the conversation export payload, containing a top-level 'sessions' list.
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

    def list_sessions(self) -> tuple[ExportedConversationSession, ...]:
        """Downloads all conversation export objects and returns typed exported sessions."""
        try:
            objects = list(self._client.list_objects(self._bucket, prefix=_CONVERSATIONS_PREFIX, recursive=True))
        except S3Error as exc:
            raise ConversationAnalysisError(f"Cannot list objects in bucket '{self._bucket}': {exc}") from exc

        sessions_by_id: dict[str, ExportedConversationSession] = {}
        for obj in objects:
            for session in self._load_sessions_from_object(obj.object_name):
                sessions_by_id[str(session.session_id)] = session  # latest export wins
        return tuple(sessions_by_id.values())

    def _load_sessions_from_object(self, object_name: str) -> tuple[ExportedConversationSession, ...]:
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

        sessions = payload.get("sessions", [])
        if not isinstance(sessions, list):
            raise ConversationAnalysisError(f"Invalid sessions payload in object '{object_name}'.")
        return tuple(self._to_exported_session(session_payload, object_name) for session_payload in sessions)

    def _to_exported_session(self, payload: object, object_name: str) -> ExportedConversationSession:
        if not isinstance(payload, dict):
            raise ConversationAnalysisError(f"Invalid session payload in object '{object_name}'.")

        raw_session_id = payload.get("id")
        if not isinstance(raw_session_id, str):
            raise ConversationAnalysisError(f"Missing session id in object '{object_name}'.")

        try:
            session_id = SessionId(value=UUID(raw_session_id))
        except (TypeError, ValueError) as exc:
            raise ConversationAnalysisError(
                f"Invalid session id '{raw_session_id}' in object '{object_name}'."
            ) from exc

        raw_messages = payload.get("messages", [])
        if not isinstance(raw_messages, list):
            raise ConversationAnalysisError(f"Invalid messages payload for session '{raw_session_id}' in '{object_name}'.")

        return ExportedConversationSession(
            session_id=session_id,
            messages=tuple(self._to_exported_message(message_payload, object_name, raw_session_id) for message_payload in raw_messages),
        )

    def _to_exported_message(
        self,
        payload: object,
        object_name: str,
        raw_session_id: str,
    ) -> ExportedConversationMessage:
        if not isinstance(payload, dict):
            raise ConversationAnalysisError(
                f"Invalid message payload for session '{raw_session_id}' in object '{object_name}'."
            )

        role = payload.get("role")
        content = payload.get("content", "")
        if not isinstance(role, str):
            raise ConversationAnalysisError(
                f"Missing message role for session '{raw_session_id}' in object '{object_name}'."
            )
        if not isinstance(content, str):
            raise ConversationAnalysisError(
                f"Invalid message content for session '{raw_session_id}' in object '{object_name}'."
            )
        return ExportedConversationMessage(role=role, content=content)
