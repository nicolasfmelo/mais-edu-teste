from __future__ import annotations

import httpx

from app.domain_models.agent.models import GatewayPromptReply, GatewayPromptRequest
from app.domain_models.common.exceptions import (
    LLMProxyConfigurationError,
    LLMProxyInsufficientCreditError,
    LLMProxyInvocationError,
    LLMProxyModelNotAllowedError,
    LLMProxyUnauthorizedError,
)


class LLMProxyGatewayClient:
    def __init__(self, base_url: str, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def generate_reply(self, request: GatewayPromptRequest) -> GatewayPromptReply:
        if not self._base_url:
            raise LLMProxyConfigurationError("LLM proxy base URL is not configured.")

        try:
            with httpx.Client(base_url=self._base_url, timeout=self._timeout_seconds) as client:
                response = client.post(
                    "/v1/llm/invoke",
                    headers={
                        "content-type": "application/json",
                        "x-api-key": request.api_key,
                        "x-idempotency-key": request.idempotency_key,
                    },
                    json={
                        "model_id": request.model_id,
                        "input": {
                            "prompt": request.prompt,
                        },
                    },
                )
        except httpx.HTTPError as exc:
            raise LLMProxyInvocationError("Failed to reach the LLM proxy.") from exc

        if response.status_code in {401}:
            raise LLMProxyUnauthorizedError("The provided API key is missing or invalid.")
        if response.status_code == 402:
            raise LLMProxyInsufficientCreditError("The provided API key has insufficient credit.")
        if response.status_code == 400:
            error_code = response.json().get("error")
            if error_code == "model_not_allowed":
                raise LLMProxyModelNotAllowedError("The selected model is not allowed by the proxy.")
            raise LLMProxyInvocationError(f"Invalid LLM invoke request: {error_code or 'bad_request'}.")
        if response.status_code >= 500:
            raise LLMProxyInvocationError("The LLM proxy failed to complete the invoke request.")
        if response.status_code >= 300:
            raise LLMProxyInvocationError(f"Unexpected LLM proxy status: {response.status_code}.")

        payload = response.json()
        return GatewayPromptReply(
            content=self._extract_text(payload),
            model_id=payload.get("model_id"),
            provider_latency_ms=payload.get("provider_latency_ms"),
        )

    def _extract_text(self, payload: dict[str, object]) -> str:
        response = payload.get("response")
        if not isinstance(response, dict):
            return ""
        output = response.get("output")
        if not isinstance(output, dict):
            return ""
        message = output.get("message")
        if not isinstance(message, dict):
            return ""
        content = message.get("content")
        if not isinstance(content, list):
            return ""

        texts: list[str] = []
        for part in content:
            if isinstance(part, dict):
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    texts.append(text)

        return "\n".join(texts).strip()
