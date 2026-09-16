"""
Input contracts for GradNavi AI-assisted operations.

WBS 6.2 defines four supported operations:

1. Resume generation
2. Cover-letter generation
3. Interview-question generation
4. Interview-answer feedback

These Pydantic models validate data before prompt construction.

User-supplied job descriptions and interview answers stay classified
as untrusted content even after structural validation.
"""

from pydantic import Field

from ai_services.schemas.common import (
    AIContractModel,
    SHORT_TEXT_MAX_LENGTH,
    StudentProfileContext,
)


# ---------------------------------------------------------------------------
# WBS 6.2 input limits
# ---------------------------------------------------------------------------

JOB_DESCRIPTION_MAX_LENGTH = 20_000
INTERVIEW_QUESTION_MAX_LENGTH = 2_000
STUDENT_ANSWER_MAX_LENGTH = 10_000

DEFAULT_INTERVIEW_QUESTION_COUNT = 5
MIN_INTERVIEW_QUESTION_COUNT = 1
MAX_INTERVIEW_QUESTION_COUNT = 10


class ResumeGenerationInput(AIContractModel):
    """
    Validated input for resume-draft generation.

    Resume generation uses approved Student Profile facts only.

    Job-description context is intentionally excluded because FR-08
    defines resume generation from Student Profile data. Job-description
    matching belongs to separate project scope.
    """

    profile: StudentProfileContext


class CoverLetterGenerationInput(AIContractModel):
    """
    Validated input for cover-letter generation.

    job_description is user-supplied and must stay classified as
    untrusted content during prompt construction.
    """

    profile: StudentProfileContext

    job_description: str = Field(
        min_length=1,
        max_length=JOB_DESCRIPTION_MAX_LENGTH,
    )


class InterviewQuestionInput(AIContractModel):
    """
    Validated input for interview-question generation.

    Full Student Profile data is intentionally excluded.

    target_role provides the main interview context.

    job_description is optional and, when supplied, stays classified
    as untrusted content.

    question_count controls how many questions GradNavi requests.
    """

    target_role: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    job_description: str | None = Field(
        default=None,
        min_length=1,
        max_length=JOB_DESCRIPTION_MAX_LENGTH,
    )

    question_count: int = Field(
        default=DEFAULT_INTERVIEW_QUESTION_COUNT,
        ge=MIN_INTERVIEW_QUESTION_COUNT,
        le=MAX_INTERVIEW_QUESTION_COUNT,
    )


class InterviewFeedbackInput(AIContractModel):
    """
    Validated input for interview-answer feedback.

    Full Student Profile data is intentionally excluded.

    The Student answer stays classified as untrusted content during
    prompt construction.
    """

    target_role: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    question: str = Field(
        min_length=1,
        max_length=INTERVIEW_QUESTION_MAX_LENGTH,
    )

    student_answer: str = Field(
        min_length=1,
        max_length=STUDENT_ANSWER_MAX_LENGTH,
    )