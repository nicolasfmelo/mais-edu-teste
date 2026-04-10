from __future__ import annotations

from fastapi import FastAPI

from app.bootstrap.container import AppContainer


def create_application() -> FastAPI:
    container = AppContainer()
    application = FastAPI(title="Mais A Educ Backend", version="0.1.0")
    application.include_router(container.build_router())
    return application


app = create_application()
