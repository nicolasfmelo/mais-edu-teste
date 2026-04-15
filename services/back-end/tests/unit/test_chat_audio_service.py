from app.domain_models.chat.models import ChatAudioRequest, ChatResponse, ChatMessage, MessageRole
from app.domain_models.common.ids import MessageId, SessionId
from app.services.chat.chat_audio_service import ChatAudioService


class StubChatService:
    def __init__(self) -> None:
        self.last_request = None

    def handle_message(self, chat_request):  # noqa: ANN001
        self.last_request = chat_request
        return ChatResponse(
            session_id=chat_request.session_id,
            reply=ChatMessage(
                id=MessageId.new(),
                role=MessageRole.ASSISTANT,
                content="Resposta do assistente",
            ),
        )


class StubAudioTranscriber:
    def transcribe(self, *, audio_bytes: bytes, filename: str, language: str | None = None) -> str:
        assert audio_bytes == b"audio"
        assert filename == "audio.webm"
        assert language == "pt"
        return "quero curso de dados"


def test_chat_audio_service_transcribes_audio_and_reuses_chat_flow() -> None:
    chat_service = StubChatService()
    service = ChatAudioService(
        chat_service=chat_service,
        audio_transcriber=StubAudioTranscriber(),
    )
    session_id = SessionId.new()

    response = service.handle_audio_message(
        ChatAudioRequest(
            session_id=session_id,
            audio_bytes=b"audio",
            audio_filename="audio.webm",
            api_key="key_test",
            language="pt",
        )
    )

    assert response.session_id == session_id
    assert response.transcription == "quero curso de dados"
    assert response.reply.content == "Resposta do assistente"
    assert chat_service.last_request is not None
    assert chat_service.last_request.message.role == MessageRole.USER
    assert chat_service.last_request.message.content == "quero curso de dados"
