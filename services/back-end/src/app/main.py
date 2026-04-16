from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.bootstrap.container import AppContainer
from app.bootstrap.observability import configure_structured_logging, install_observability
from app.domain_models.common.exceptions import (
    BackendDomainError,
    AudioTranscriptionError,
    ConversationAnalysisError,
    ConversationExportError,
    LLMProxyConfigurationError,
    LLMProxyInsufficientCreditError,
    LLMProxyInvocationError,
    LLMProxyModelNotAllowedError,
    LLMProxyUnauthorizedError,
)
from app.domain_models.prompt.exceptions import PromptAlreadyExistsError, PromptRegistryEntryNotFoundError


def _resolve_cors_origins(container: object) -> list[str]:
    settings = getattr(container, "_settings", None)
    origins = getattr(settings, "cors_allowed_origins", ("*"))
    return list(origins)


def create_application(container: AppContainer | None = None) -> FastAPI:
    app_container = container or AppContainer()
    settings = getattr(app_container, "_settings", None)
    configure_structured_logging(
        level=getattr(settings, "log_level", "INFO"),
        output_format=getattr(settings, "log_format", "json"),
    )
    app_container.startup()
    application = FastAPI(title="Mais A Educ Backend", version="0.1.0")
    application.state.container = app_container
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
    application.add_exception_handler(PromptRegistryEntryNotFoundError, _handle_prompt_not_found_error)
    application.add_exception_handler(PromptAlreadyExistsError, _handle_prompt_conflict_error)
    application.add_exception_handler(BackendDomainError, _handle_backend_domain_error)
    application.add_exception_handler(AudioTranscriptionError, _handle_audio_transcription_error)
    application.add_exception_handler(ConversationExportError, _handle_conversation_export_error)
    application.add_exception_handler(ConversationAnalysisError, _handle_conversation_analysis_error)
    application.include_router(app_container.build_router())
    install_observability(application)
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


async def _handle_prompt_not_found_error(_: Request, exc: PromptRegistryEntryNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": str(exc)})


async def _handle_prompt_conflict_error(_: Request, exc: PromptAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"error": str(exc)})


async def _handle_backend_domain_error(_: Request, exc: BackendDomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": str(exc)})


async def _handle_audio_transcription_error(_: Request, exc: AudioTranscriptionError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"error": str(exc)})


async def _handle_conversation_export_error(_: Request, exc: ConversationExportError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"error": str(exc)})


async def _handle_conversation_analysis_error(_: Request, exc: ConversationAnalysisError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"error": str(exc)})
