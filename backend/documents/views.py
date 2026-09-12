from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_services.exceptions import AIServiceError
from documents.providers import get_resume_generation_provider
from documents.serializers import (
    ResumeDraftSerializer,
    ResumeGenerationRequestSerializer,
)
from documents.services.resume_generation import generate_resume_draft
from profiles.models import StudentProfile


class ExternalServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = (
        "The requested service is temporarily unavailable. "
        "Please try again later."
    )
    default_code = "external_service_unavailable"


class ResumeGenerationView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ResumeGenerationRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        try:
            profile = self._get_profile(request.user)
            ai_provider = get_resume_generation_provider()
            resume_draft = generate_resume_draft(
                student_profile=profile,
                ai_provider=ai_provider,
            )
        except AIServiceError as exc:
            raise ExternalServiceUnavailable() from exc

        return Response(
            {
                "data": {
                    "resume_draft": ResumeDraftSerializer(
                        resume_draft,
                    ).data,
                }
            }
        )

    def _get_profile(self, user):
        try:
            return (
                StudentProfile.objects.prefetch_related(
                    "student_skills__skill",
                    "education",
                    "experience",
                    "projects",
                    "career_goals",
                )
                .order_by("id")
                .get(user=user)
            )
        except StudentProfile.DoesNotExist:
            raise NotFound("Student profile was not found.")
