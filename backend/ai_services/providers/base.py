"""
Provider-independent AI service contract for GradNavi.

WBS 6.2 defines the interface used by AI-assisted feature services.

This module does not connect to OpenAI or any other external provider.

WBS 7.3 will later implement a concrete provider behind this contract.
"""

from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

from ai_services.prompts.common import PromptPackage


OutputModelT = TypeVar(
    "OutputModelT",
    bound=BaseModel,
)


@runtime_checkable
class AIProvider(Protocol):
    """
    Provider-independent contract for GradNavi AI generation.

    prompt_package
        Provider-independent GradNavi prompt structure.

    output_model
        Pydantic model class used to validate the expected provider result.

    The concrete provider must return a validated instance of output_model.

    Provider-specific request conversion, credentials, retries, timeouts,
    and external API execution belong to later Sprint 4 work.
    """

    def generate(
        self,
        *,
        prompt_package: PromptPackage,
        output_model: type[OutputModelT],
    ) -> OutputModelT:
        """
        Generate and validate one AI-assisted result.
        """
        ...