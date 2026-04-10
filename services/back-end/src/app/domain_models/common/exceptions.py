class BackendDomainError(Exception):
    """Base class for domain errors."""


class SessionNotFoundError(BackendDomainError):
    """Raised when a chat session cannot be found."""


class CreditUnavailableError(BackendDomainError):
    """Raised when credits cannot be verified."""


class KnowledgeUnavailableError(BackendDomainError):
    """Raised when the knowledge base cannot be queried."""
