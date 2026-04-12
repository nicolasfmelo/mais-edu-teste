from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header

from app.delivery.schemas.assistant_catalog_schemas import (
    AssistantModelListResponseSchema,
    CreditBalanceResponseSchema,
)
from app.services.agent.assistant_catalog_service import AssistantCatalogService


class AssistantCatalogHandler:
    def __init__(self, assistant_catalog_service: AssistantCatalogService) -> None:
        self._assistant_catalog_service = assistant_catalog_service
        self.router = APIRouter(tags=["assistant-catalog"])
        self.router.add_api_route(
            "/api/credits/balance",
            self.get_credit_balance,
            methods=["GET"],
            response_model=CreditBalanceResponseSchema,
        )
        self.router.add_api_route(
            "/api/assistant-models",
            self.list_models,
            methods=["GET"],
            response_model=AssistantModelListResponseSchema,
        )

    async def get_credit_balance(
        self,
        x_api_key: Annotated[str, Header(alias="x-api-key", min_length=1)],
    ) -> CreditBalanceResponseSchema:
        return CreditBalanceResponseSchema.from_domain(
            self._assistant_catalog_service.get_credit_balance(api_key=x_api_key)
        )

    async def list_models(self) -> AssistantModelListResponseSchema:
        return AssistantModelListResponseSchema.from_domain(self._assistant_catalog_service.list_models())
