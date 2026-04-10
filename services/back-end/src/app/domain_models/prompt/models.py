from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class PromptKey:
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PromptVersionId:
    value: UUID

    @classmethod
    def new(cls) -> "PromptVersionId":
        return cls(value=uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class PromptVersion:
    id: PromptVersionId
    version_number: int
    template: str
    description: str
    is_active: bool = False


@dataclass(frozen=True)
class PromptRegistryEntry:
    key: PromptKey
    versions: tuple[PromptVersion, ...] = field(default_factory=tuple)

    def active_version(self) -> PromptVersion | None:
        for version in self.versions:
            if version.is_active:
                return version
        return None


@dataclass(frozen=True)
class PromptRegistration:
    key: PromptKey
    template: str
    description: str


@dataclass(frozen=True)
class PromptVersionRegistration:
    key: PromptKey
    template: str
    description: str


@dataclass(frozen=True)
class PromptActivation:
    key: PromptKey
    version_id: PromptVersionId
