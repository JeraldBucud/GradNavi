"""
Interview preparation service layer for GradNavi.

WBS 6.6 provides two AI-assisted operations:

1. Interview question generation
2. Interview answer feedback

This service layer uses the provider-independent AIProvider contract
defined in WBS 6.2.

Direct external AI provider integration belongs to WBS 7.3.
"""

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

    return ai_provider.generate(
        prompt_package=prompt_package,
        output_model=InterviewQuestionSet,
    )


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