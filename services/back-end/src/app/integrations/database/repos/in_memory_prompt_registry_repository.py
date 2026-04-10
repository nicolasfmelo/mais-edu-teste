from __future__ import annotations

from app.domain_models.prompt.exceptions import (
    PromptAlreadyExistsError,
    PromptRegistryEntryNotFoundError,
)
from app.domain_models.prompt.models import (
    PromptActivation,
    PromptKey,
    PromptRegistration,
    PromptRegistryEntry,
    PromptVersion,
    PromptVersionId,
    PromptVersionRegistration,
)
from app.engines.prompt.prompt_engine import PromptEngine


class InMemoryPromptRegistryRepository:
    def __init__(self, prompt_engine: PromptEngine) -> None:
        self._prompt_engine = prompt_engine
        self._entries: dict[str, PromptRegistryEntry] = {}

    def list_entries(self) -> tuple[PromptRegistryEntry, ...]:
        return tuple(sorted(self._entries.values(), key=lambda entry: entry.key.value))

    def find_by_key(self, key: PromptKey) -> PromptRegistryEntry:
        entry = self._entries.get(key.value)
        if entry is None:
            raise PromptRegistryEntryNotFoundError(f"Prompt {key} not found")
        return entry

    def create_prompt(self, registration: PromptRegistration) -> PromptRegistryEntry:
        if registration.key.value in self._entries:
            raise PromptAlreadyExistsError(f"Prompt {registration.key} already exists")

        first_version = PromptVersion(
            id=PromptVersionId.new(),
            version_number=1,
            template=registration.template,
            description=registration.description,
            is_active=True,
        )
        entry = PromptRegistryEntry(key=registration.key, versions=(first_version,))
        self._entries[registration.key.value] = entry
        return entry

    def create_version(self, registration: PromptVersionRegistration) -> PromptRegistryEntry:
        current_entry = self.find_by_key(registration.key)
        next_version_number = len(current_entry.versions) + 1
        new_version = PromptVersion(
            id=PromptVersionId.new(),
            version_number=next_version_number,
            template=registration.template,
            description=registration.description,
            is_active=False,
        )
        updated_entry = PromptRegistryEntry(
            key=current_entry.key,
            versions=(*current_entry.versions, new_version),
        )
        self._entries[registration.key.value] = updated_entry
        return updated_entry

    def activate_version(self, activation: PromptActivation) -> PromptRegistryEntry:
        entry = self.find_by_key(activation.key)
        updated_entry = self._prompt_engine.activate_version(entry, activation)
        self._entries[activation.key.value] = updated_entry
        return updated_entry
