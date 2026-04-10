from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.domain_models.prompt.models import PromptRegistryEntry, PromptVersion


class PromptVersionResponseSchema(BaseModel):
    id: UUID
    version_number: int
    template: str
    description: str
    is_active: bool

    @classmethod
    def from_domain(cls, version: PromptVersion) -> "PromptVersionResponseSchema":
        return cls(
            id=version.id.value,
            version_number=version.version_number,
            template=version.template,
            description=version.description,
            is_active=version.is_active,
        )


class PromptRegistryEntryResponseSchema(BaseModel):
    key: str
    active_version_id: UUID | None
    versions: list[PromptVersionResponseSchema]

    @classmethod
    def from_domain(cls, entry: PromptRegistryEntry) -> "PromptRegistryEntryResponseSchema":
        active_version = entry.active_version()
        return cls(
            key=entry.key.value,
            active_version_id=active_version.id.value if active_version else None,
            versions=[PromptVersionResponseSchema.from_domain(version) for version in entry.versions],
        )


class PromptRegistryListResponseSchema(BaseModel):
    items: list[PromptRegistryEntryResponseSchema]

    @classmethod
    def from_domain(cls, entries: tuple[PromptRegistryEntry, ...]) -> "PromptRegistryListResponseSchema":
        return cls(items=[PromptRegistryEntryResponseSchema.from_domain(entry) for entry in entries])


class RegisterPromptRequestSchema(BaseModel):
    key: str = Field(min_length=1)
    template: str = Field(min_length=1)
    description: str = Field(min_length=1)


class CreatePromptVersionRequestSchema(BaseModel):
    template: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ActivatePromptVersionRequestSchema(BaseModel):
    version_id: UUID


class ActivePromptVersionResponseSchema(BaseModel):
    key: str
    version: PromptVersionResponseSchema

    @classmethod
    def from_domain(cls, key: str, version: PromptVersion) -> "ActivePromptVersionResponseSchema":
        return cls(key=key, version=PromptVersionResponseSchema.from_domain(version))
