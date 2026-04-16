import httpx
import pytest

from app.domain_models.common.exceptions import LLMProxyInvocationError, LLMProxyUnauthorizedError
from app.integrations.external_apis.llm_proxy_gateway_client import LLMProxyGatewayClient


def test_normalize_base_url_strips_v1_suffix() -> None:
    client = LLMProxyGatewayClient(base_url="https://example.com/v1")
    assert client._base_url == "https://example.com"


def test_normalize_base_url_keeps_host_path_when_not_v1_suffix() -> None:
    client = LLMProxyGatewayClient(base_url="https://example.com/prod")
    assert client._base_url == "https://example.com/prod"


def test_raise_for_status_maps_404_api_key_not_found_to_unauthorized() -> None:
    client = LLMProxyGatewayClient(base_url="https://example.com")
    response = httpx.Response(
        status_code=404,
        request=httpx.Request("GET", "https://example.com/v1/credits/balance"),
        json={"error": "api_key_not_found"},
    )

    with pytest.raises(LLMProxyUnauthorizedError):
        client._raise_for_status(response)


def test_raise_for_status_maps_unexpected_404_to_invocation_error() -> None:
    client = LLMProxyGatewayClient(base_url="https://example.com")
    response = httpx.Response(
        status_code=404,
        request=httpx.Request("GET", "https://example.com/v1/credits/balance"),
        text="Not Found",
    )

    with pytest.raises(LLMProxyInvocationError, match="endpoint not found"):
        client._raise_for_status(response)
