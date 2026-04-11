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
