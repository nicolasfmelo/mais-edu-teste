from __future__ import annotations

from uuid import UUID

from app.domain_models.common.contracts import PromptRegistryRepository
from app.domain_models.prompt.models import (
    PromptActivation,
    PromptRegistration,
    PromptRegistryEntry,
    PromptVersion,
    PromptVersionId,
    PromptVersionRegistration,
)
from app.engines.prompt.prompt_engine import PromptEngine


class PromptRegistryService:
    def __init__(
        self,
        prompt_registry_repository: PromptRegistryRepository,
        prompt_engine: PromptEngine,
    ) -> None:
        self._prompt_registry_repository = prompt_registry_repository
        self._prompt_engine = prompt_engine

    def list_prompts(self) -> tuple[PromptRegistryEntry, ...]:
        return self._prompt_registry_repository.list_entries()

    def get_prompt(self, raw_key: str) -> PromptRegistryEntry:
        return self._prompt_registry_repository.find_by_key(self._prompt_engine.normalize_key(raw_key))

    def register_prompt(self, raw_key: str, template: str, description: str) -> PromptRegistryEntry:
        registration = PromptRegistration(
            key=self._prompt_engine.normalize_key(raw_key),
            template=template,
            description=description,
        )
        return self._prompt_registry_repository.create_prompt(registration)

    def ensure_prompt(self, raw_key: str, template: str, description: str) -> PromptRegistryEntry:
        registration = PromptRegistration(
            key=self._prompt_engine.normalize_key(raw_key),
            template=template,
            description=description,
        )
        return self._prompt_registry_repository.ensure_prompt(registration)

    def create_version(self, raw_key: str, template: str, description: str) -> PromptRegistryEntry:
        registration = PromptVersionRegistration(
            key=self._prompt_engine.normalize_key(raw_key),
            template=template,
            description=description,
        )
        return self._prompt_registry_repository.create_version(registration)

    def get_active_version(self, raw_key: str) -> PromptVersion:
        entry = self.get_prompt(raw_key)
        return self._prompt_engine.resolve_active_version(entry)

    def activate_version(self, raw_key: str, raw_version_id: str) -> PromptRegistryEntry:
        activation = PromptActivation(
            key=self._prompt_engine.normalize_key(raw_key),
            version_id=PromptVersionId(value=UUID(raw_version_id)),
        )
        entry = self._prompt_registry_repository.find_by_key(activation.key)
        activated_entry = self._prompt_engine.activate_version(entry, activation)
        return self._prompt_registry_repository.activate_version(activated_entry)
