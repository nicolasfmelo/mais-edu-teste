from __future__ import annotations

from app.domain_models.prompt.exceptions import InvalidPromptKeyError, PromptVersionNotFoundError
from app.domain_models.prompt.models import PromptActivation, PromptKey, PromptRegistryEntry, PromptVersion


class PromptEngine:
    """Pure rules for prompt registry normalization and version activation."""

    def normalize_key(self, raw_key: str) -> PromptKey:
        normalized = raw_key.strip().lower().replace(" ", "-").replace("_", "-")
        if not normalized:
            raise InvalidPromptKeyError("Prompt key cannot be empty")
        return PromptKey(value=normalized)

    def activate_version(
        self,
        entry: PromptRegistryEntry,
        activation: PromptActivation,
    ) -> PromptRegistryEntry:
        updated_versions: list[PromptVersion] = []
        selected = False

        for version in entry.versions:
            is_target = version.id == activation.version_id
            updated_versions.append(
                PromptVersion(
                    id=version.id,
                    version_number=version.version_number,
                    template=version.template,
                    description=version.description,
                    is_active=is_target,
                )
            )
            if is_target:
                selected = True

        if not selected:
            raise PromptVersionNotFoundError(
                f"Version {activation.version_id} not found for prompt {entry.key}"
            )

        return PromptRegistryEntry(key=entry.key, versions=tuple(updated_versions))

    def resolve_active_version(self, entry: PromptRegistryEntry) -> PromptVersion:
        active_version = entry.active_version()
        if active_version is None:
            raise PromptVersionNotFoundError(f"Active version not found for prompt {entry.key}")
        return active_version
