"""
Interview AI-provider dependency seam.

WBS 7.3 connects Interview Question and Interview Feedback operations
to the shared GradNavi OpenAI text provider.

Interview services stay provider-independent and continue to use the
existing AIProvider contract from WBS 6.2.
"""

from ai_services.providers.base import AIProvider
from ai_services.providers.openai_text import OpenAITextProvider


def get_interview_provider() -> AIProvider:
    """
    Return the configured provider for Interview AI operations.
    """

    return OpenAITextProvider()