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
from urllib.parse import urlparse

from pydantic import (
    Field,
    field_validator,
    model_validator,
)

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


class CareerMatchExplanation(AIContractModel):
    """
    Short grounded explanation for one deterministic Career Recommendation.

    AI may explain supplied evidence only.

    It must never replace or modify the deterministic recommendation score,
    rank, readiness score, or Skill Gap calculations.
    """

    explanation: str = Field(
        min_length=1,
        max_length=600,
    )

    is_ai_generated: Literal[True]


class SkillGapSummaryExplanation(AIContractModel):
    """
    Grounded natural-language explanation of an
    already-calculated Skill Gap Analysis.

    AI does not calculate or alter readiness or gap statuses.
    """

    readiness_explanation: str = Field(
        min_length=1,
        max_length=800,
    )

    recommended_next_steps: list[str]

    is_ai_generated: Literal[True]

class RoadmapGuidanceItem(AIContractModel):
    """
    Personalised explanation for one deterministic
    Career Roadmap step.

    The Skill name is supplied by GradNavi.

    AI explains the step only.
    """

    skill_name: str = Field(
        min_length=1,
        max_length=255,
    )

    why_this_matters: str = Field(
        min_length=1,
        max_length=800,
    )

    your_focus: str = Field(
        min_length=1,
        max_length=600,
    )


class RoadmapGuidanceExplanation(AIContractModel):
    """
    Personalised guidance for the deterministic
    top Career Roadmap steps.

    AI must not change the Skill list or ordering.
    """

    guidance_items: list[
        RoadmapGuidanceItem
    ] = Field(
        min_length=1,
        max_length=3,
    )

    is_ai_generated: Literal[True]

class LearningResourceGuidanceItem(AIContractModel):
    """
    Personalised explanation for one deterministic
    Learning Resource recommendation.

    AI writes explanation text only.
    """

    resource_id: int = Field(
        gt=0,
    )

    why_this_fits: str = Field(
        min_length=1,
        max_length=700,
    )


class LearningResourceGuidanceExplanation(
    AIContractModel
):
    """
    Personalised explanations for the strongest
    deterministic Learning Resource recommendations.

    AI must not add, remove, rank, or reorder resources.
    """

    guidance_items: list[
        LearningResourceGuidanceItem
    ] = Field(
        min_length=1,
        max_length=6,
    )

    is_ai_generated: Literal[True]


class DiscoveredLearningResourceCandidate(
    AIContractModel
):
    """
    One externally discovered Learning Resource candidate.

    The URL is treated as untrusted external data and must
    use HTTP or HTTPS before later validation and persistence.
    """

    title: str = Field(
        min_length=1,
        max_length=255,
    )

    provider: str = Field(
        min_length=1,
        max_length=255,
    )

    url: str = Field(
        min_length=1,
        max_length=2_000,
    )

    resource_type: Literal[
        "course",
        "documentation",
        "article",
        "video",
        "tutorial",
        "book",
        "other",
    ]

    access_type: Literal[
        "free",
        "freemium",
        "paid",
        "unknown",
    ]

    description: str = Field(
        min_length=1,
        max_length=1_000,
    )

    @field_validator(
        "url"
    )
    @classmethod
    def validate_resource_url(
        cls,
        value,
    ):
        parsed = urlparse(
            value
        )

        if (
            parsed.scheme
            not in {
                "http",
                "https",
            }
            or not parsed.netloc
        ):
            raise ValueError(
                "Resource URL must use HTTP or HTTPS."
            )

        return value


class LearningResourceDiscoveryResult(
    AIContractModel
):
    """
    Structured Learning Resource discovery result.

    Zero candidates is valid when no suitable real
    resource was found.
    """

    candidates: list[
        DiscoveredLearningResourceCandidate
    ] = Field(
        max_length=6,
    )

    is_ai_generated: Literal[True]

    @model_validator(
        mode="after"
    )
    def validate_unique_urls(
        self,
    ):
        normalized_urls = [
            item.url
            .strip()
            .casefold()
            for item
            in self.candidates
        ]

        if (
            len(
                normalized_urls
            )
            != len(
                set(
                    normalized_urls
                )
            )
        ):
            raise ValueError(
                "Discovered resource URLs must be unique."
            )

        return self
