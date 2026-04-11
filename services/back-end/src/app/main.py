from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bootstrap.container import AppContainer


def create_application(container: AppContainer | None = None) -> FastAPI:
    app_container = container or AppContainer()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        app_container.startup()
        application.state.container = app_container
        yield

    application = FastAPI(title="Mais A Educ Backend", version="0.1.0", lifespan=lifespan)
    application.include_router(app_container.build_router())
    return application


app = create_application()
