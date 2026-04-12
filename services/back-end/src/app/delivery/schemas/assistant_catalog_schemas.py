from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain_models.agent.models import AssistantModel, CreditBalance


class CreditBalanceResponseSchema(BaseModel):
    available: int
    checked_at: datetime

    @classmethod
    def from_domain(cls, balance: CreditBalance) -> "CreditBalanceResponseSchema":
        return cls(
            available=balance.available,
            checked_at=balance.checked_at,
        )


class AssistantModelSchema(BaseModel):
    key: str
    label: str
    provider: str
    is_default: bool
    status: str

    @classmethod
    def from_domain(cls, model: AssistantModel) -> "AssistantModelSchema":
        return cls(
            key=model.key,
            label=model.label,
            provider=model.provider,
            is_default=model.is_default,
            status=model.status,
        )


class AssistantModelListResponseSchema(BaseModel):
    items: list[AssistantModelSchema]

    @classmethod
    def from_domain(cls, models: tuple[AssistantModel, ...]) -> "AssistantModelListResponseSchema":
        return cls(items=[AssistantModelSchema.from_domain(model) for model in models])
