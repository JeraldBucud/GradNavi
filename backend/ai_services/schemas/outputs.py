"""
Validated output contracts for GradNavi AI-assisted operations.

WBS 6.2 treats AI-provider responses as untrusted external input.

Provider output must match one of these Pydantic models before later
GradNavi feature services treat the generated content as structurally
valid application data.

These contracts provide structural validation only.

Provider-specific parsing, retry behaviour, and deeper semantic response
validation remain part of later Sprint 4 work.
"""

from typing import Literal

from pydantic import Field

from ai_services.schemas.common import AIContractModel


# ---------------------------------------------------------------------------
# WBS 6.2 output limits
# ---------------------------------------------------------------------------

GENERATED_TEXT_MAX_LENGTH = 5_000
GENERATED_SHORT_TEXT_MAX_LENGTH = 1_000

MAX_RESUME_SKILLS = 100
MAX_RESUME_EDUCATION_ITEMS = 20
MAX_RESUME_EXPERIENCE_ITEMS = 30
MAX_RESUME_PROJECT_ITEMS = 30

MAX_COVER_LETTER_PARAGRAPHS = 10
MAX_MATCHED_PROFILE_FACTS = 50

MAX_INTERVIEW_QUESTIONS = 10
MAX_INTERVIEW_FOCUS_AREAS = 20

MAX_FEEDBACK_ITEMS = 20
MAX_MISSING_INFORMATION_ITEMS = 50
MAX_LIMITATION_ITEMS = 20


class ResumeDraft(AIContractModel):
    """
    Structured editable resume draft.

    Identity and contact information stay outside the generative layer.

    is_draft and requires_user_review are fixed to True so AI-generated
    document content cannot be represented as a final approved document.
    """

    professional_summary: str = Field(
        min_length=1,
        max_length=GENERATED_TEXT_MAX_LENGTH,
    )

    skills: list[str] = Field(
        max_length=MAX_RESUME_SKILLS,
    )

    education: list[str] = Field(
        max_length=MAX_RESUME_EDUCATION_ITEMS,
    )

    experience: list[str] = Field(
        max_length=MAX_RESUME_EXPERIENCE_ITEMS,
    )

    projects: list[str] = Field(
        max_length=MAX_RESUME_PROJECT_ITEMS,
    )

    missing_information: list[str] = Field(
        max_length=MAX_MISSING_INFORMATION_ITEMS,
    )

    limitations: list[str] = Field(
        max_length=MAX_LIMITATION_ITEMS,
    )

    is_draft: Literal[True]

    requires_user_review: Literal[True]


class CoverLetterDraft(AIContractModel):
    """
    Structured editable cover-letter draft.

    body_paragraphs uses a list so the frontend receives predictable
    editable document sections rather than one uncontrolled text block.
    """

    opening: str = Field(
        min_length=1,
        max_length=GENERATED_TEXT_MAX_LENGTH,
    )

    body_paragraphs: list[str] = Field(
        min_length=1,
        max_length=MAX_COVER_LETTER_PARAGRAPHS,
    )

    closing: str = Field(
        min_length=1,
        max_length=GENERATED_TEXT_MAX_LENGTH,
    )

    matched_profile_facts: list[str] = Field(
        max_length=MAX_MATCHED_PROFILE_FACTS,
    )

    missing_information: list[str] = Field(
        max_length=MAX_MISSING_INFORMATION_ITEMS,
    )

    limitations: list[str] = Field(
        max_length=MAX_LIMITATION_ITEMS,
    )

    is_draft: Literal[True]

    requires_user_review: Literal[True]


class InterviewQuestion(AIContractModel):
    """
    One generated interview-preparation question.
    """

    question: str = Field(
        min_length=1,
        max_length=GENERATED_TEXT_MAX_LENGTH,
    )

    focus_area: str = Field(
        min_length=1,
        max_length=GENERATED_SHORT_TEXT_MAX_LENGTH,
    )


class InterviewQuestionSet(AIContractModel):
    """
    Structured set of generated interview questions.

    No hiring probability or pass/fail result belongs in this contract.
    """

    questions: list[InterviewQuestion] = Field(
        min_length=1,
        max_length=MAX_INTERVIEW_QUESTIONS,
    )

    focus_areas: list[str] = Field(
        max_length=MAX_INTERVIEW_FOCUS_AREAS,
    )

    limitations: list[str] = Field(
        max_length=MAX_LIMITATION_ITEMS,
    )

    is_ai_generated: Literal[True]

    requires_user_review: Literal[True]


class InterviewFeedback(AIContractModel):
    """
    Structured feedback for one typed Student interview answer.

    This contract intentionally excludes hiring probabilities,
    pass/fail classifications, and guaranteed employment outcomes.
    """

    strengths: list[str] = Field(
        max_length=MAX_FEEDBACK_ITEMS,
    )

    improvements: list[str] = Field(
        max_length=MAX_FEEDBACK_ITEMS,
    )

    suggested_response: str = Field(
        min_length=1,
        max_length=GENERATED_TEXT_MAX_LENGTH,
    )

    feedback_summary: str = Field(
        min_length=1,
        max_length=GENERATED_TEXT_MAX_LENGTH,
    )

    limitations: list[str] = Field(
        max_length=MAX_LIMITATION_ITEMS,
    )

    is_ai_generated: Literal[True]

    requires_user_review: Literal[True]