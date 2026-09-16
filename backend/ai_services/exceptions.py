"""
Shared exception hierarchy for GradNavi AI services.

WBS 6.2 defines provider-independent error categories used by AI-assisted
features.

These exceptions do not contain provider-specific handling.

OpenAI-specific error translation, retry behaviour, timeout handling, and
response parsing belong to later Sprint 4 work.
"""


class AIServiceError(Exception):
    """
    Base exception for GradNavi AI-service failures.
    """


class AIInputError(AIServiceError):
    """
    Raised when an AI operation receives invalid application input.
    """


class AIMissingContextError(AIInputError):
    """
    Raised when an AI operation lacks required application context.
    """


class AISafetyError(AIServiceError):
    """
    Raised when an AI operation violates an approved safety rule.
    """


class AIPrivacyError(AIServiceError):
    """
    Raised when data does not satisfy the approved AI privacy boundary.
    """


class AIProviderError(AIServiceError):
    """
    Base exception for failures involving an external AI provider.
    """


class AIProviderUnavailableError(AIProviderError):
    """
    Raised when the configured AI provider is unavailable.
    """


class AIProviderTimeoutError(AIProviderError):
    """
    Raised when an AI-provider request exceeds the configured timeout.
    """


class AIResponseValidationError(AIProviderError):
    """
    Raised when provider output fails GradNavi response validation.
    """


class AIUnsupportedOperationError(AIServiceError):
    """
    Raised when an unsupported AI operation is requested.
    """