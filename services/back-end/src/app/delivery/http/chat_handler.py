from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from starlette.datastructures import UploadFile

from app.delivery.schemas.chat_schemas import (
    ChatAudioMessageResponseSchema,
    ChatMessageRequestSchema,
    ChatMessageResponseSchema,
    ChatSessionDetailResponseSchema,
    ChatSessionListResponseSchema,
    ChatSessionSummarySchema,
)
from app.domain_models.chat.models import ChatAudioRequest
from app.domain_models.common.ids import SessionId
from app.services.chat.chat_audio_service import ChatAudioService
from app.services.chat.chat_service import ChatService


class ChatHandler:
    def __init__(self, chat_service: ChatService, chat_audio_service: ChatAudioService, max_audio_bytes: int) -> None:
        self._chat_service = chat_service
        self._chat_audio_service = chat_audio_service
        self._max_audio_bytes = max_audio_bytes
        self.router = APIRouter(prefix="/api/chat", tags=["chat"])
        self.router.add_api_route("/sessions", self.list_sessions, methods=["GET"], response_model=ChatSessionListResponseSchema)
        self.router.add_api_route("/sessions", self.create_session, methods=["POST"], response_model=ChatSessionSummarySchema)
        self.router.add_api_route(
            "/sessions/{session_id}",
            self.get_session,
            methods=["GET"],
            response_model=ChatSessionDetailResponseSchema,
        )
        self.router.add_api_route("/messages", self.post_message, methods=["POST"], response_model=ChatMessageResponseSchema)
        self.router.add_api_route(
            "/audio-messages",
            self.post_audio_message,
            methods=["POST"],
            response_model=ChatAudioMessageResponseSchema,
        )

    async def list_sessions(self) -> ChatSessionListResponseSchema:
        return ChatSessionListResponseSchema.from_domain(self._chat_service.list_sessions())

    async def create_session(self) -> ChatSessionSummarySchema:
        return ChatSessionSummarySchema.from_domain(self._chat_service.create_session())

    async def get_session(self, session_id: UUID) -> ChatSessionDetailResponseSchema:
        return ChatSessionDetailResponseSchema.from_domain(self._chat_service.get_session(SessionId(value=session_id)))

    async def post_message(self, body: ChatMessageRequestSchema) -> ChatMessageResponseSchema:
        response = self._chat_service.handle_message(body.to_domain())
        return ChatMessageResponseSchema.from_domain(response)

    async def post_audio_message(
        self,
        request: Request,
    ) -> ChatAudioMessageResponseSchema:
        form = await request.form()
        session_id_raw = form.get("session_id")
        api_key_raw = form.get("api_key")
        model_id = self._to_optional_text(form.get("model_id"))
        system_prompt = self._to_optional_text(form.get("system_prompt"))
        language = self._to_optional_text(form.get("language"))
        audio = form.get("audio")

        if not isinstance(session_id_raw, str):
            raise HTTPException(status_code=400, detail="session_id e obrigatorio.")
        if not isinstance(api_key_raw, str) or not api_key_raw.strip():
            raise HTTPException(status_code=400, detail="api_key e obrigatorio.")
        try:
            session_id = UUID(session_id_raw)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="session_id invalido.") from exc
        if not isinstance(audio, UploadFile):
            raise HTTPException(status_code=400, detail="Arquivo de audio e obrigatorio.")
        if not audio.filename:
            raise HTTPException(status_code=400, detail="O arquivo de audio deve possuir nome.")
        if audio.content_type and not audio.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Formato de arquivo invalido. Envie um arquivo de audio.")

        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="O arquivo de audio enviado esta vazio.")
        if len(audio_bytes) > self._max_audio_bytes:
            raise HTTPException(status_code=413, detail="Arquivo de audio excede o limite permitido.")

        response = self._chat_audio_service.handle_audio_message(
            ChatAudioRequest(
                session_id=SessionId(value=session_id),
                audio_bytes=audio_bytes,
                audio_filename=audio.filename,
                audio_content_type=audio.content_type,
                api_key=api_key_raw.strip(),
                model_id=model_id,
                system_prompt=system_prompt,
                language=language,
            )
        )
        return ChatAudioMessageResponseSchema.from_domain(response)

    def _to_optional_text(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        cleaned = value.strip()
        return cleaned or None
