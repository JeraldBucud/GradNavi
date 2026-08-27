from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudentProfile
from .serializers import StudentProfileSerializer, StudentProfileUpdateSerializer


class StudentProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = self._get_profile(request.user)
        return Response({"data": {"profile": StudentProfileSerializer(profile).data}})

    def patch(self, request):
        profile = self._get_profile(request.user)
        serializer = StudentProfileUpdateSerializer(
            data=request.data,
            context={"profile": profile},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        profile = self._get_profile(request.user)
        return Response({"data": {"profile": StudentProfileSerializer(profile).data}})

    def _get_profile(self, user):
        try:
            return (
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
                .get(user=user)
            )
        except StudentProfile.DoesNotExist:
            raise NotFound("Student profile was not found.")
