"""
Interview AI provider dependency seam.

Concrete external provider configuration belongs to WBS 7.3.

Until provider integration exists, the Interview API fails closed
instead of returning fabricated production responses.
"""

from ai_services.exceptions import AIProviderUnavailableError
from ai_services.providers.base import AIProvider


def get_interview_provider() -> AIProvider:
    """
    Return the configured provider for interview AI operations.

    WBS 7.3 will replace this fail-closed implementation with the
    configured external provider.
    """

    raise AIProviderUnavailableError(
        "AI provider is not configured for interview preparation."
    )