from pathlib import Path

from fastapi.testclient import TestClient

from app.bootstrap.container import AppContainer
from app.bootstrap.settings import AppSettings
from app.main import create_application


def test_prompt_registry_routes_support_registration_versioning_and_activation(tmp_path: Path) -> None:
    with TestClient(
        create_application(
            container=AppContainer(
                settings=AppSettings(
                    database_url=f"sqlite+pysqlite:///{tmp_path / 'routes.db'}",
                    datasets_dir=tmp_path / "datasets",
                    indexing_bootstrap_enabled=False,
                    llm_proxy_base_url="https://example.invalid",
                    minio_access_key="test-access-key",
                    minio_secret_key="test-secret-key",
                )
            )
        )
    ) as client:
        created = client.post(
            "/api/prompt-registry/prompts",
            json={
                "key": "sales-qualification",
                "template": "template v1",
                "description": "initial version",
            },
        )
        assert created.status_code == 200
        created_body = created.json()
        assert created_body["key"] == "sales-qualification"
        assert created_body["versions"][0]["is_active"] is True

        second_version = client.post(
            "/api/prompt-registry/prompts/sales-qualification/versions",
            json={
                "template": "template v2",
                "description": "second version",
            },
        )
        assert second_version.status_code == 200
        second_version_id = second_version.json()["versions"][1]["id"]

        activate = client.post(
            "/api/prompt-registry/prompts/sales-qualification/active",
            json={"version_id": second_version_id},
        )
        assert activate.status_code == 200
        assert activate.json()["versions"][1]["is_active"] is True

        active = client.get("/api/prompt-registry/prompts/sales-qualification/active")
        assert active.status_code == 200
        assert active.json()["version"]["id"] == second_version_id


def test_prompt_registry_returns_404_for_missing_prompt_key(tmp_path: Path) -> None:
    with TestClient(
        create_application(
            container=AppContainer(
                settings=AppSettings(
                    database_url=f"sqlite+pysqlite:///{tmp_path / 'routes-missing.db'}",
                    datasets_dir=tmp_path / "datasets",
                    indexing_bootstrap_enabled=False,
                    llm_proxy_base_url="https://example.invalid",
                    minio_access_key="test-access-key",
                    minio_secret_key="test-secret-key",
                )
            )
        )
    ) as client:
        response = client.get("/api/prompt-registry/prompts/prompt-that-does-not-exist")

        assert response.status_code == 404


def test_prompt_registry_seeds_default_agent_prompts_on_startup(tmp_path: Path) -> None:
    with TestClient(
        create_application(
            container=AppContainer(
                settings=AppSettings(
                    database_url=f"sqlite+pysqlite:///{tmp_path / 'routes-seeded.db'}",
                    datasets_dir=tmp_path / "datasets",
                    indexing_bootstrap_enabled=False,
                    llm_proxy_base_url="https://example.invalid",
                    minio_access_key="test-access-key",
                    minio_secret_key="test-secret-key",
                )
            )
        )
    ) as client:
        chat_prompt = client.get("/api/prompt-registry/prompts/chat-agent-system")
        nps_prompt = client.get("/api/prompt-registry/prompts/nps-agent-system")

        assert chat_prompt.status_code == 200
        assert nps_prompt.status_code == 200
        assert chat_prompt.json()["versions"][0]["is_active"] is True
        assert nps_prompt.json()["versions"][0]["is_active"] is True
