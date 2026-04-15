from pathlib import Path

from fastapi.testclient import TestClient

from app.bootstrap.container import AppContainer
from app.bootstrap.settings import AppSettings
from app.domain_models.agent.models import GatewayPromptReply
from app.main import create_application


def test_chat_routes_support_listing_loading_and_sending_messages(tmp_path: Path) -> None:
    container = AppContainer(
        settings=AppSettings(
            database_url=f"sqlite+pysqlite:///{tmp_path / 'chat-routes.db'}",
            datasets_dir=tmp_path / "datasets",
            indexing_bootstrap_enabled=False,
            llm_proxy_base_url="https://example.invalid",
            cors_allowed_origins=("http://localhost:5173",),
            minio_access_key="test-access-key",
            minio_secret_key="test-secret-key",
        )
    )
    container._ai_gateway_client.generate_reply = lambda request: GatewayPromptReply(  # type: ignore[method-assign]
        content=f"Resposta simulada para: {request.prompt[:20]}",
        model_id=request.model_id,
        provider_latency_ms=12,
    )

    with TestClient(create_application(container=container)) as client:
        created = client.post("/api/chat/sessions")
        assert created.status_code == 200
        created_body = created.json()
        session_id = created_body["id"]
        assert created_body["message_count"] == 0

        listed_empty = client.get("/api/chat/sessions")
        assert listed_empty.status_code == 200
        assert listed_empty.json()["items"][0]["id"] == session_id

        loaded_empty = client.get(f"/api/chat/sessions/{session_id}")
        assert loaded_empty.status_code == 200
        assert loaded_empty.json()["messages"] == []

        sent = client.post(
            "/api/chat/messages",
            json={
                "session_id": session_id,
                "message": "Quero uma sugestao de curso remoto.",
                "api_key": "key_test",
            },
        )
        assert sent.status_code == 200, sent.text
        sent_body = sent.json()
        assert sent_body["session_id"] == session_id
        assert sent_body["assistant_message"]["role"] == "assistant"
        assert sent_body["assistant_message"]["content"].startswith("Resposta simulada para:")

        loaded = client.get(f"/api/chat/sessions/{session_id}")
        assert loaded.status_code == 200
        loaded_body = loaded.json()
        assert loaded_body["session"]["message_count"] == 2
        assert [message["role"] for message in loaded_body["messages"]] == ["user", "assistant"]

        listed = client.get("/api/chat/sessions")
        assert listed.status_code == 200
        listed_body = listed.json()
        assert listed_body["items"][0]["message_count"] == 2
        assert listed_body["items"][0]["preview"].startswith("Resposta simulada para:")


def test_chat_audio_messages_route_transcribes_and_sends_to_agent(tmp_path: Path) -> None:
    container = AppContainer(
        settings=AppSettings(
            database_url=f"sqlite+pysqlite:///{tmp_path / 'chat-audio-routes.db'}",
            datasets_dir=tmp_path / "datasets",
            indexing_bootstrap_enabled=False,
            llm_proxy_base_url="https://example.invalid",
            cors_allowed_origins=("http://localhost:5173",),
            minio_access_key="test-access-key",
            minio_secret_key="test-secret-key",
        )
    )
    container._ai_gateway_client.generate_reply = lambda request: GatewayPromptReply(  # type: ignore[method-assign]
        content=f"Resposta simulada para: {request.prompt[:20]}",
        model_id=request.model_id,
        provider_latency_ms=12,
    )
    container._audio_transcriber.transcribe = lambda **_: "Quero um curso de tecnologia."  # type: ignore[method-assign]

    with TestClient(create_application(container=container)) as client:
        created = client.post("/api/chat/sessions")
        assert created.status_code == 200
        session_id = created.json()["id"]

        sent_audio = client.post(
            "/api/chat/audio-messages",
            data={
                "session_id": session_id,
                "api_key": "key_test",
                "language": "pt",
            },
            files={"audio": ("audio.webm", b"fake-audio-content", "audio/webm")},
        )
        assert sent_audio.status_code == 200, sent_audio.text
        sent_audio_body = sent_audio.json()
        assert sent_audio_body["session_id"] == session_id
        assert sent_audio_body["transcription"] == "Quero um curso de tecnologia."
        assert sent_audio_body["assistant_message"]["role"] == "assistant"
        assert sent_audio_body["assistant_message"]["content"].startswith("Resposta simulada para:")
