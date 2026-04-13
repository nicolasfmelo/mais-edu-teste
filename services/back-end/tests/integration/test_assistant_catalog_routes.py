from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.bootstrap.container import AppContainer
from app.bootstrap.settings import AppSettings
from app.domain_models.agent.models import CreditBalance
from app.main import create_application


def test_assistant_catalog_routes_expose_models_and_current_credit_balance(tmp_path: Path) -> None:
    container = AppContainer(
        settings=AppSettings(
            database_url=f"sqlite+pysqlite:///{tmp_path / 'assistant-catalog-routes.db'}",
            datasets_dir=tmp_path / "datasets",
            indexing_bootstrap_enabled=False,
            llm_proxy_base_url="https://example.invalid",
            cors_allowed_origins=("http://localhost:5173",),
            minio_access_key="test-access-key",
            minio_secret_key="test-secret-key",
        )
    )
    container._ai_gateway_client.get_credit_balance = lambda api_key: CreditBalance(  # type: ignore[method-assign]
        available=19,
        checked_at=datetime(2026, 4, 11, 22, 0, tzinfo=UTC),
    )

    with TestClient(create_application(container=container)) as client:
        models = client.get("/api/assistant-models")
        assert models.status_code == 200, models.text
        models_body = models.json()
        assert models_body["items"][0]["key"] == "us.anthropic.claude-sonnet-4-6"
        assert models_body["items"][0]["is_default"] is True
        assert models_body["items"][1]["provider"] == "anthropic"

        credits = client.get(
            "/api/credits/balance",
            headers={"x-api-key": "key_test"},
        )
        assert credits.status_code == 200, credits.text
        assert credits.json() == {
            "available": 19,
            "checked_at": "2026-04-11T22:00:00Z",
        }
