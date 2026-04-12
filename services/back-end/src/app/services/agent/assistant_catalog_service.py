from __future__ import annotations

from app.domain_models.agent.models import AssistantModel, CreditBalance
from app.domain_models.common.contracts import CreditBalanceClient


class AssistantCatalogService:
    def __init__(
        self,
        credit_balance_client: CreditBalanceClient,
        assistant_models: tuple[AssistantModel, ...],
    ) -> None:
        self._credit_balance_client = credit_balance_client
        self._assistant_models = assistant_models

    def get_credit_balance(self, api_key: str) -> CreditBalance:
        return self._credit_balance_client.get_credit_balance(api_key)

    def list_models(self) -> tuple[AssistantModel, ...]:
        return self._assistant_models
