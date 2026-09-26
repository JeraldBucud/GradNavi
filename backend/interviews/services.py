"""
Interview preparation service layer for GradNavi.

WBS 6.6 provides two AI-assisted operations:

1. Interview question generation
2. Interview answer feedback

This service layer uses the provider-independent AIProvider contract
defined in WBS 6.2.

WBS 7.3 provides external AI provider integration.

WBS 7.4 adds semantic response validation before generated Interview
Question results leave this service layer.
"""

from ai_services.exceptions import (
    AIResponseValidationError,
)
from ai_services.prompts.interview_feedback import (
    build_interview_feedback_prompt,
)
from ai_services.prompts.interview_questions import (
    build_interview_question_prompt,
)
from ai_services.providers.base import AIProvider
from ai_services.schemas.inputs import (
    DEFAULT_INTERVIEW_QUESTION_COUNT,
    InterviewFeedbackInput,
    InterviewQuestionInput,
)
from ai_services.schemas.outputs import (
    InterviewFeedback,
    InterviewQuestionSet,
)


def _normalize_focus_area(
    value: str,
) -> str:
    """
    Normalize one focus-area value for semantic comparison only.

    The original provider output is never rewritten.
    """

    return (
        value
        .strip()
        .casefold()
    )


def _validate_interview_question_set(
    *,
    result: InterviewQuestionSet,
    requested_question_count: int,
) -> None:
    """
    Enforce WBS 7.4 Interview Question response semantics.

    Structural validation is already performed by InterviewQuestionSet.

    This layer verifies that the external AI result agrees with the
    application request and with its own focus-area summary.

    Invalid provider output is rejected rather than silently corrected.
    """

    if (
        len(
            result.questions
        )
        != requested_question_count
    ):
        raise AIResponseValidationError(
            "Interview AI response question count does not "
            "match the requested count."
        )

    question_focus_areas = []

    for question in result.questions:

        normalized = (
            _normalize_focus_area(
                question.focus_area
            )
        )

        if not normalized:
            raise AIResponseValidationError(
                "Interview AI response contains a blank "
                "question focus area."
            )

        question_focus_areas.append(
            normalized
        )

    declared_focus_areas = []
    declared_seen = set()

    for focus_area in result.focus_areas:

        normalized = (
            _normalize_focus_area(
                focus_area
            )
        )

        if not normalized:
            raise AIResponseValidationError(
                "Interview AI response contains a blank "
                "declared focus area."
            )

        if normalized in declared_seen:
            raise AIResponseValidationError(
                "Interview AI response contains duplicate "
                "declared focus areas."
            )

        declared_seen.add(
            normalized
        )

        declared_focus_areas.append(
            normalized
        )

    expected_focus_areas = set(
        question_focus_areas
    )

    actual_focus_areas = set(
        declared_focus_areas
    )

    if (
        actual_focus_areas
        != expected_focus_areas
    ):
        raise AIResponseValidationError(
            "Interview AI response focus areas do not "
            "match generated questions."
        )


def generate_interview_questions(
    *,
    target_role: str,
    ai_provider: AIProvider,
    job_description: str | None = None,
    question_count: int = DEFAULT_INTERVIEW_QUESTION_COUNT,
) -> InterviewQuestionSet:
    """
    Generate a validated set of interview preparation questions.

    Input validation is delegated to InterviewQuestionInput.

    Prompt construction is delegated to the shared WBS 6.2
    interview-question prompt builder.

    The supplied AI provider must return a validated
    InterviewQuestionSet.
    """

    request = InterviewQuestionInput(
        target_role=target_role,
        job_description=job_description,
        question_count=question_count,
    )

    prompt_package = build_interview_question_prompt(
        request
    )

    result = ai_provider.generate(
        prompt_package=prompt_package,
        output_model=InterviewQuestionSet,
    )

    _validate_interview_question_set(
        result=result,
        requested_question_count=(
            request.question_count
        ),
    )

    return result


def generate_interview_feedback(
    *,
    target_role: str,
    question: str,
    student_answer: str,
    ai_provider: AIProvider,
) -> InterviewFeedback:
    """
    Generate validated feedback for one typed interview answer.

    Input validation is delegated to InterviewFeedbackInput.

    Prompt construction is delegated to the shared WBS 6.2
    interview-feedback prompt builder.

    The supplied AI provider must return validated
    InterviewFeedback.
    """

    request = InterviewFeedbackInput(
        target_role=target_role,
        question=question,
        student_answer=student_answer,
    )

    prompt_package = build_interview_feedback_prompt(
        request
    )

    return ai_provider.generate(
        prompt_package=prompt_package,
        output_model=InterviewFeedback,
    )
