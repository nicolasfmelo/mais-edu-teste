from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.main import create_application


class StubContainer:
    def __init__(self) -> None:
        self.started = False

    def build_router(self) -> APIRouter:
        return APIRouter()

    def startup(self) -> None:
        self.started = True


def test_application_runs_container_startup_on_lifespan() -> None:
    container = StubContainer()

    with TestClient(create_application(container=container)) as client:
        response = client.get("/metrics")

    assert container.started is True
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "x-request-id" in response.headers
