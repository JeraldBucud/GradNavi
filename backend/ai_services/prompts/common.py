"""
Shared prompt contracts for GradNavi AI-assisted features.

WBS 6.2 gives every AI operation the same prompt-section structure.

Provider-specific conversion belongs to WBS 7.3.
"""

from dataclasses import dataclass
from enum import StrEnum


class AIOperation(StrEnum):
    """
    Approved GradNavi AI operations.

    Feature services use these fixed operation identifiers instead of
    arbitrary strings.
    """

    RESUME_GENERATION = "resume_generation"
    COVER_LETTER_GENERATION = "cover_letter_generation"
    INTERVIEW_QUESTION_GENERATION = "interview_question_generation"
    INTERVIEW_FEEDBACK = "interview_feedback"


@dataclass(frozen=True)
class PromptPackage:
    """
    Provider-independent GradNavi prompt package.

    system_instructions
        Trusted application-controlled instructions.

    safety_rules
        Shared GradNavi AI safety requirements.

    trusted_context
        Validated application context prepared by GradNavi.

    untrusted_content
        User-controlled content kept separate from trusted instructions.

    output_requirements
        Required response-format instructions.
    """

    operation: AIOperation
    system_instructions: tuple[str, ...]
    safety_rules: tuple[str, ...]
    trusted_context: str
    untrusted_content: str
    output_requirements: tuple[str, ...]


def _render_instruction_list(
    *,
    heading: str,
    values: tuple[str, ...],
) -> str:
    """
    Render one numbered prompt section.
    """

    if not values:
        return f"{heading}\nNone"

    rendered_values = "\n".join(
        f"{index}. {value}"
        for index, value in enumerate(values, start=1)
    )

    return f"{heading}\n{rendered_values}"


def render_prompt_package(
    package: PromptPackage,
) -> str:
    """
    Render a PromptPackage using the approved WBS 6.2 section order.

    The rendering format stays provider-independent.
    """

    sections = (
        _render_instruction_list(
            heading="SYSTEM INSTRUCTIONS",
            values=package.system_instructions,
        ),
        _render_instruction_list(
            heading="GRADNAVI SAFETY RULES",
            values=package.safety_rules,
        ),
        (
            "OPERATION\n"
            f"{package.operation.value}"
        ),
        (
            "TRUSTED STRUCTURED CONTEXT\n"
            f"{package.trusted_context}"
        ),
        (
            "UNTRUSTED USER CONTENT\n"
            f"{package.untrusted_content}"
        ),
        _render_instruction_list(
            heading="OUTPUT REQUIREMENTS",
            values=package.output_requirements,
        ),
    )

    return "\n\n".join(sections)