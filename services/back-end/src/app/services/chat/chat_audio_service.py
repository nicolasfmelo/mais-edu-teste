from __future__ import annotations

from app.domain_models.chat.models import ChatAudioRequest, ChatAudioResponse, ChatMessage, ChatRequest, MessageRole
from app.domain_models.common.contracts import AudioTranscriber
from app.domain_models.common.exceptions import AudioTranscriptionError
from app.domain_models.common.ids import MessageId
from app.services.chat.chat_service import ChatService


class ChatAudioService:
    def __init__(self, chat_service: ChatService, audio_transcriber: AudioTranscriber) -> None:
        self._chat_service = chat_service
        self._audio_transcriber = audio_transcriber

    def handle_audio_message(self, audio_request: ChatAudioRequest) -> ChatAudioResponse:
        transcription = self._audio_transcriber.transcribe(
            audio_bytes=audio_request.audio_bytes,
            filename=audio_request.audio_filename,
            language=audio_request.language,
        ).strip()
        if not transcription:
            raise AudioTranscriptionError("Nao foi possivel transcrever o audio enviado.")

        chat_response = self._chat_service.handle_message(
            ChatRequest(
                session_id=audio_request.session_id,
                message=self._build_user_message(transcription),
                api_key=audio_request.api_key,
                model_id=audio_request.model_id,
                system_prompt=audio_request.system_prompt,
            )
        )

        return ChatAudioResponse(
            session_id=chat_response.session_id,
            transcription=transcription,
            reply=chat_response.reply,
        )

    def _build_user_message(self, transcription: str) -> ChatMessage:
        return ChatMessage(
            id=MessageId.new(),
            role=MessageRole.USER,
            content=transcription,
        )
