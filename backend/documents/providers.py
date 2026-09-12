"""
Documents AI-provider dependency seam.

Concrete provider configuration belongs to WBS 7.3. Until then, the
documents API fails closed without creating a fake production provider.
"""

from ai_services.exceptions import AIProviderUnavailableError
from ai_services.providers.base import AIProvider


def get_resume_generation_provider() -> AIProvider:
    """
    Return the configured resume-generation provider.
    """

    raise AIProviderUnavailableError(
        "AI provider is not configured for resume generation."
    )


def get_cover_letter_generation_provider() -> AIProvider:
    """
    Return the configured cover-letter-generation provider.
    """

    raise AIProviderUnavailableError(
        "AI provider is not configured for cover-letter generation."
    )

