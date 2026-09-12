"""
REST API views for GradNavi interview preparation.

WBS 6.6 exposes:

1. Interview question generation
2. Interview answer feedback

Both endpoints require authentication.

External AI provider execution remains outside WBS 6.6.
WBS 7.3 will provide the concrete provider implementation.
"""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_services.exceptions import AIProviderError
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