from __future__ import annotations

import httpx

from app.domain_models.agent.models import CreditBalance, GatewayPromptReply, GatewayPromptRequest
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

    def get_credit_balance(self, api_key: str) -> CreditBalance:
        payload = self._request_json(
            method="GET",
            path="/v1/credits/balance",
            headers={
                "x-api-key": api_key,
            },
        )
        return self._parse_credit_balance(payload)

    def generate_reply(self, request: GatewayPromptRequest) -> GatewayPromptReply:
        payload = self._request_json(
            method="POST",
            path="/v1/llm/invoke",
            headers={
                "content-type": "application/json",
                "x-api-key": request.api_key,
                "x-idempotency-key": request.idempotency_key,
            },
            json=self._build_invoke_payload(request),
        )
        return self._parse_gateway_reply(payload)

    def _build_invoke_payload(self, request: GatewayPromptRequest) -> dict[str, object]:
        return {
            "model_id": request.model_id,
            "input": {
                "prompt": request.prompt,
            },
        }

    def _request_json(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str],
        json: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return self._request(
            method=method,
            path=path,
            headers=headers,
            json=json,
        ).json()

    def _parse_credit_balance(self, payload: dict[str, object]) -> CreditBalance:
        remaining_credits = payload.get("remaining_credits")
        if not isinstance(remaining_credits, int):
            raise LLMProxyInvocationError("The LLM proxy returned an invalid credit balance payload.")
        return CreditBalance(available=remaining_credits)

    def _parse_gateway_reply(self, payload: dict[str, object]) -> GatewayPromptReply:
        model_id = payload.get("model_id")
        provider_latency_ms = payload.get("provider_latency_ms")
        response = payload.get("response") or {}
        usage = response.get("usage") if isinstance(response, dict) else None
        prompt_tokens = usage.get("inputTokens") if isinstance(usage, dict) else None
        completion_tokens = usage.get("outputTokens") if isinstance(usage, dict) else None
        return GatewayPromptReply(
            content=self._extract_text(payload),
            model_id=model_id if isinstance(model_id, str) else None,
            provider_latency_ms=provider_latency_ms if isinstance(provider_latency_ms, int) else None,
            prompt_tokens=prompt_tokens if isinstance(prompt_tokens, int) else None,
            completion_tokens=completion_tokens if isinstance(completion_tokens, int) else None,
        )

    def _request(
        self,
        *,
        method: str,
        path: str,
        headers: dict[str, str],
        json: dict[str, object] | None = None,
    ) -> httpx.Response:
        if not self._base_url:
            raise LLMProxyConfigurationError("LLM proxy base URL is not configured.")

        try:
            with httpx.Client(base_url=self._base_url, timeout=self._timeout_seconds) as client:
                response = client.request(
                    method,
                    path,
                    headers=headers,
                    json=json,
                )
        except httpx.HTTPError as exc:
            raise LLMProxyInvocationError("Failed to reach the LLM proxy.") from exc

        self._raise_for_status(response)
        return response

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code in {401, 404}:
            raise LLMProxyUnauthorizedError("The provided API key is missing or invalid.")
        if response.status_code == 402:
            raise LLMProxyInsufficientCreditError("The provided API key has insufficient credit.")
        if response.status_code == 400:
            error_code = self._extract_error_code(response)
            if error_code == "model_not_allowed":
                raise LLMProxyModelNotAllowedError("The selected model is not allowed by the proxy.")
            raise LLMProxyInvocationError(f"Invalid LLM proxy request: {error_code or 'bad_request'}.")
        if response.status_code >= 500:
            raise LLMProxyInvocationError("The LLM proxy failed to complete the request.")
        if response.status_code >= 300:
            raise LLMProxyInvocationError(f"Unexpected LLM proxy status: {response.status_code}.")

    def _extract_error_code(self, response: httpx.Response) -> str | None:
        payload = response.json()
        error_code = payload.get("error")
        return error_code if isinstance(error_code, str) else None

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
