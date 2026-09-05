from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from careers.serializers import RecommendationResultSerializer
from careers.services.recommendation_scoring import generate_recommendations
from profiles.models import StudentProfile


class RecommendationListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = self._get_profile(request.user)
        recommendations = generate_recommendations(
            student_profile_id=profile.id,
        )
        serializer = RecommendationResultSerializer(
            recommendations,
            many=True,
        )
        return Response(
            {
                "data": {
                    "recommendations": serializer.data,
                }
            }
        )

    def _get_profile(self, user):
        try:
            return StudentProfile.objects.get(
                user=user,
            )
        except StudentProfile.DoesNotExist:
            raise NotFound("Student profile was not found.")
