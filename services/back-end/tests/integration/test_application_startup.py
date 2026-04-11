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

    with TestClient(create_application(container=container)):
        pass

    assert container.started is True
