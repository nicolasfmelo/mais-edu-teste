from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


_HTTP_REQUEST_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the backend.",
    ("method", "route", "status_code"),
)
_HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "route"),
    buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0),
)


def configure_structured_logging(*, level: str, output_format: str) -> None:
    normalized_level = level.upper()
    normalized_format = output_format.lower()
    log_level = getattr(logging, normalized_level, logging.INFO)
    renderer: structlog.types.Processor
    if normalized_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    shared_processors: list[structlog.types.Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            *shared_processors,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.propagate = True


async def metrics_endpoint() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def install_observability(application: FastAPI) -> None:
    application.middleware("http")(_request_observability_middleware)
    application.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)


def _resolve_route_pattern(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    return route_path if isinstance(route_path, str) else request.url.path


async def _request_observability_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    started_at = time.perf_counter()
    logger = structlog.get_logger("app.http")
    client_host = request.client.host if request.client else None

    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - started_at
        route = _resolve_route_pattern(request)
        _record_request_metrics(method=request.method, route=route, status_code=500, duration=duration)
        logger.exception(
            "http_request_failed",
            request_id=request_id,
            method=request.method,
            route=route,
            path=request.url.path,
            status_code=500,
            duration_ms=round(duration * 1000, 2),
            client_ip=client_host,
        )
        raise

    duration = time.perf_counter() - started_at
    route = _resolve_route_pattern(request)
    _record_request_metrics(method=request.method, route=route, status_code=response.status_code, duration=duration)
    logger.info(
        "http_request_completed",
        request_id=request_id,
        method=request.method,
        route=route,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2),
        client_ip=client_host,
    )
    response.headers.setdefault("x-request-id", request_id)
    return response


def _record_request_metrics(*, method: str, route: str, status_code: int, duration: float) -> None:
    _HTTP_REQUEST_TOTAL.labels(method=method, route=route, status_code=str(status_code)).inc()
    _HTTP_REQUEST_DURATION_SECONDS.labels(method=method, route=route).observe(duration)
