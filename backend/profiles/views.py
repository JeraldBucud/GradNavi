from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudentProfile
from .serializers import StudentProfileSerializer


class StudentProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            profile = (
                StudentProfile.objects.prefetch_related(
                    "student_skills__skill",
                    "student_interests__interest",
                    "education",
                    "experience",
                    "projects",
                    "career_goals",
                    "personality_responses",
                )
                .order_by("id")
                .get(user=request.user)
            )
        except StudentProfile.DoesNotExist:
            raise NotFound("Student profile was not found.")

        return Response({"data": {"profile": StudentProfileSerializer(profile).data}})
