class BackendDomainError(Exception):
    """Base class for domain errors."""


class SessionNotFoundError(BackendDomainError):
    """Raised when a chat session cannot be found."""


class CreditUnavailableError(BackendDomainError):
    """Raised when credits cannot be verified."""


class KnowledgeUnavailableError(BackendDomainError):
    """Raised when the knowledge base cannot be queried."""


class LLMProxyConfigurationError(BackendDomainError):
    """Raised when the LLM proxy integration is not configured."""


class LLMProxyUnauthorizedError(BackendDomainError):
    """Raised when the provided API key is missing or invalid."""


class LLMProxyInsufficientCreditError(BackendDomainError):
    """Raised when the provided API key has no remaining credits."""


class LLMProxyModelNotAllowedError(BackendDomainError):
    """Raised when the selected model is not allowed by the proxy."""


class LLMProxyInvocationError(BackendDomainError):
    """Raised when the LLM proxy fails to complete the invoke."""
