from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.bootstrap.container import AppContainer
from app.domain_models.common.exceptions import (
    BackendDomainError,
    LLMProxyConfigurationError,
    LLMProxyInsufficientCreditError,
    LLMProxyInvocationError,
    LLMProxyModelNotAllowedError,
    LLMProxyUnauthorizedError,
)


def _resolve_cors_origins(container: object) -> list[str]:
    settings = getattr(container, "_settings", None)
    origins = getattr(settings, "cors_allowed_origins", ("http://0.0.0.0:5173", "http://localhost:5173"))
    return list(origins)


def create_application(container: AppContainer | None = None) -> FastAPI:
    app_container = container or AppContainer()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        app_container.startup()
        application.state.container = app_container
        yield

    application = FastAPI(title="Mais A Educ Backend", version="0.1.0", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_resolve_cors_origins(app_container),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_exception_handler(LLMProxyUnauthorizedError, _handle_unauthorized_llm_error)
    application.add_exception_handler(LLMProxyInsufficientCreditError, _handle_credit_llm_error)
    application.add_exception_handler(LLMProxyModelNotAllowedError, _handle_invalid_model_llm_error)
    application.add_exception_handler(LLMProxyConfigurationError, _handle_configuration_llm_error)
    application.add_exception_handler(LLMProxyInvocationError, _handle_invoke_llm_error)
    application.add_exception_handler(BackendDomainError, _handle_backend_domain_error)
    application.include_router(app_container.build_router())
    return application


async def _handle_unauthorized_llm_error(_: Request, exc: LLMProxyUnauthorizedError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"error": str(exc)})


async def _handle_credit_llm_error(_: Request, exc: LLMProxyInsufficientCreditError) -> JSONResponse:
    return JSONResponse(status_code=402, content={"error": str(exc)})


async def _handle_invalid_model_llm_error(_: Request, exc: LLMProxyModelNotAllowedError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


async def _handle_configuration_llm_error(_: Request, exc: LLMProxyConfigurationError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": str(exc)})


async def _handle_invoke_llm_error(_: Request, exc: LLMProxyInvocationError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"error": str(exc)})


async def _handle_backend_domain_error(_: Request, exc: BackendDomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})
