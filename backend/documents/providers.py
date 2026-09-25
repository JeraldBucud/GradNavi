"""
Documents AI-provider dependency seam.

WBS 7.3 connects Resume and Cover Letter generation to the shared
GradNavi OpenAI text provider.

Feature services stay provider-independent and receive the provider
through the existing AIProvider contract.
"""

from ai_services.providers.base import AIProvider
from ai_services.providers.openai_text import OpenAITextProvider


def get_resume_generation_provider() -> AIProvider:
    """
    Return the configured provider for Resume generation.
    """

    return OpenAITextProvider()


def get_cover_letter_generation_provider() -> AIProvider:
    """
    Return the configured provider for Cover Letter generation.
    """

    return OpenAITextProvider()