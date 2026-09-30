"""
REST API views for GradNavi interview preparation.

WBS 6.6 exposes:

1. Interview question generation
2. Interview answer feedback

Both endpoints require authentication.

WBS 7.3 connects these endpoints to the shared OpenAI text provider
through the existing provider-independent AI service boundary.
"""

import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_services.exceptions import (
    AIProviderError,
    AIResponseValidationError,
)
from interviews.providers import get_interview_provider
from interviews.serializers import (
    InterviewFeedbackRequestSerializer,
    InterviewFeedbackSerializer,
    InterviewQuestionRequestSerializer,
    InterviewQuestionSetSerializer,
)
from interviews.services import (
    generate_interview_feedback,
    generate_interview_questions,
)


logger = logging.getLogger(__name__)


INTERVIEW_VALIDATION_LOG_CATEGORIES = {
    (
        "OpenAI response was incomplete."
    ): "output_incomplete",
    (
        "OpenAI response did not complete successfully."
    ): "output_not_completed",
    (
        "OpenAI response did not contain structured output text."
    ): "structured_output_missing",
    (
        "OpenAI structured output failed GradNavi validation."
    ): "structured_output_invalid",
    (
        "Interview AI response question count does not "
        "match the requested count."
    ): "question_count_mismatch",
    (
        "Interview AI response contains a blank "
        "question focus area."
    ): "question_focus_area_blank",
    (
        "Interview AI response contains a blank "
        "declared focus area."
    ): "declared_focus_area_blank",
    (
        "Interview AI response contains duplicate "
        "declared focus areas."
    ): "duplicate_focus_area",
    (
        "Interview AI response focus areas do not "
        "match generated questions."
    ): "focus_area_mismatch",
    (
        "Interview AI feedback contains an "
        "unsupported placeholder value."
    ): "feedback_placeholder",
    (
        "Interview AI feedback contains an "
        "unsupported numeric claim."
    ): "feedback_unsupported_numeric_claim",
}


def _validation_failure_category(
    error: AIResponseValidationError,
) -> str:
    """
    Return a safe internal validation category.

    No generated or Student-supplied content is returned.
    """

    return INTERVIEW_VALIDATION_LOG_CATEGORIES.get(
        str(error),
        "interview_validation_failed",
    )


class InterviewServiceUnavailable(APIException):
    """
    Controlled API response for unavailable AI provider services.
    """

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = (
        "Interview preparation is temporarily unavailable. "
        "Please try again later."
    )
    default_code = "external_service_unavailable"


class InterviewResponseInvalid(APIException):
    """
    Controlled API response for invalid generated interview output.
    """

    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = (
        "The generated interview response could not be validated. "
        "Please try again."
    )
    default_code = "ai_response_invalid"


class InterviewQuestionGenerationView(APIView):
    """
    Generate interview preparation questions.

    POST /api/v1/interviews/questions/
    """

    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request):
        serializer = InterviewQuestionRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        validated_data = serializer.validated_data

        try:
            ai_provider = get_interview_provider()

            question_set = generate_interview_questions(
                target_role=validated_data[
                    "target_role"
                ],
                job_description=validated_data.get(
                    "job_description"
                ),
                question_count=validated_data[
                    "question_count"
                ],
                ai_provider=ai_provider,
            )

        except AIResponseValidationError as exc:
            logger.warning(
                "Interview question AI validation failed: %s",
                _validation_failure_category(
                    exc
                ),
            )
            raise InterviewResponseInvalid() from exc

        except AIProviderError as exc:
            raise InterviewServiceUnavailable() from exc

        response_serializer = (
            InterviewQuestionSetSerializer(
                question_set
            )
        )

        return Response(
            {
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class InterviewFeedbackGenerationView(APIView):
    """
    Generate feedback for one typed interview answer.

    POST /api/v1/interviews/feedback/
    """

    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request):
        serializer = InterviewFeedbackRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        validated_data = serializer.validated_data

        try:
            ai_provider = get_interview_provider()

            feedback = generate_interview_feedback(
                target_role=validated_data[
                    "target_role"
                ],
                question=validated_data[
                    "question"
                ],
                student_answer=validated_data[
                    "student_answer"
                ],
                ai_provider=ai_provider,
            )

        except AIResponseValidationError as exc:
            logger.warning(
                "Interview feedback AI validation failed: %s",
                _validation_failure_category(
                    exc
                ),
            )
            raise InterviewResponseInvalid() from exc

        except AIProviderError as exc:
            raise InterviewServiceUnavailable() from exc

        response_serializer = (
            InterviewFeedbackSerializer(
                feedback
            )
        )

        return Response(
            {
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
