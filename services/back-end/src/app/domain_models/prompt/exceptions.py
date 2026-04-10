from app.domain_models.common.exceptions import BackendDomainError


class PromptRegistryEntryNotFoundError(BackendDomainError):
    """Raised when a prompt key is not registered."""


class PromptVersionNotFoundError(BackendDomainError):
    """Raised when a prompt version cannot be found."""


class PromptAlreadyExistsError(BackendDomainError):
    """Raised when trying to create a prompt key that already exists."""


class InvalidPromptKeyError(BackendDomainError):
    """Raised when a prompt key is invalid."""
