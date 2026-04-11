from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.bootstrap.container import AppContainer
from app.bootstrap.settings import AppSettings
from app.main import create_application


@pytest.mark.integration
def test_chat_messages_route_can_call_live_llm_proxy(tmp_path) -> None:  # noqa: ANN001
    api_key = os.getenv("LLM_PROXY_TEST_API_KEY")
    if not api_key:
        pytest.skip("Set LLM_PROXY_TEST_API_KEY to run the live LLM proxy chat test.")

    repo_root = Path(__file__).resolve()
    for _ in range(5):
        repo_root = repo_root.parent
    datasets_dir = repo_root / "services" / "datasets"

    with TestClient(
        create_application(
            container=AppContainer(
                settings=AppSettings(
                    database_url=f"sqlite+pysqlite:///{tmp_path / 'live-chat.db'}",
                    datasets_dir=datasets_dir,
                    indexing_bootstrap_enabled=True,
                    llm_proxy_base_url=os.getenv(
                        "LLM_PROXY_BASE_URL",
                        "https://kviwmiapph.execute-api.us-east-1.amazonaws.com",
                    ),
                )
            )
        )
    ) as client:
        response = client.post(
            "/api/chat/messages",
            json={
                "session_id": str(uuid4()),
                "message": "Quero um MBA remoto em lideranca.",
                "api_key": api_key,
                "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                "system_prompt": "Atue como a Clara, consultora educacional do Instituto Horizonte Digital.",
            },
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["reply"].strip()
