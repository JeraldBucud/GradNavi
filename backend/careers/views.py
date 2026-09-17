from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from careers.serializers import (
    CareerSelectionQuerySerializer,
    CompositeRecommendationResultSerializer,
    LearningSuggestionSerializer,
    RoadmapStepSerializer,
)
from careers.services.learning_roadmap import generate_learning_plan
from ai_services.exceptions import (
    AIProviderError,
)

from ai_services.providers.openai_embeddings import (
    OpenAIEmbeddingProvider,
)

from careers.services.composite_recommendation import (
    COMPETENCY_WEIGHT,
    SEMANTIC_WEIGHT,
    TECHNOLOGY_WEIGHT,
    generate_composite_recommendations,
)
from careers.services.readiness_scoring import (
    CareerNotAvailableError,
    CareerNotFoundError,
)
from profiles.models import StudentProfile


class RecommendationAIUnavailable(APIException):
    """
    Returned when the AI embedding provider required by the
    locked WBS 5.3 composite model is unavailable.
    """

    status_code = 503

    default_detail = (
        "AI Career Recommendation scoring is "
        "currently unavailable."
    )

    default_code = (
        "ai_service_unavailable"
    )



class RecommendationListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = self._get_profile(
            request.user
        )

        try:
            embedding_provider = (
                OpenAIEmbeddingProvider()
            )

            report = (
                generate_composite_recommendations(
                    student_profile_id=(
                        profile.id
                    ),
                    embedding_provider=(
                        embedding_provider
                    ),
                )
            )

        except AIProviderError as error:
            raise RecommendationAIUnavailable() from error

        serializer = (
            CompositeRecommendationResultSerializer(
                report.results,
                many=True,
            )
        )

        return Response(
            {
                "data": {
                    "scoring_model": (
                        "composite_v1"
                    ),
                    "embedding_model": (
                        report.model
                    ),
                    "career_count": (
                        report.career_count
                    ),
                    "base_weights": {
                        "competency": str(
                            COMPETENCY_WEIGHT
                        ),
                        "technology": str(
                            TECHNOLOGY_WEIGHT
                        ),
                        "semantic": str(
                            SEMANTIC_WEIGHT
                        ),
                    },
                    "recommendations": (
                        serializer.data
                    ),
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


class LearningSuggestionListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = self._get_profile(
            request.user
        )
        career_id = self._get_career_id(
            request
        )
        plan = self._generate_plan(
            student_profile_id=profile.id,
            career_id=career_id,
        )
        serializer = LearningSuggestionSerializer(
            plan.suggestions,
            many=True,
        )

        return Response(
            {
                "data": {
                    "career_id": plan.career_id,
                    "career_name": plan.career_name,
                    "score_status": self._enum_value(
                        plan
                        .readiness_result
                        .score_status
                    ),
                    "readiness_score": (
                        self._decimal_value(
                            plan
                            .readiness_result
                            .readiness_score
                        )
                    ),
                    "learning_suggestions": (
                        serializer.data
                    ),
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

    def _get_career_id(self, request):
        serializer = CareerSelectionQuerySerializer(
            data=request.query_params,
        )
        serializer.is_valid(
            raise_exception=True,
        )
        return serializer.validated_data[
            "career_id"
        ]

    def _generate_plan(
        self,
        *,
        student_profile_id,
        career_id,
    ):
        try:
            return generate_learning_plan(
                student_profile_id=(
                    student_profile_id
                ),
                career_id=career_id,
            )
        except CareerNotFoundError:
            raise NotFound(
                "Selected career was not found."
            )
        except CareerNotAvailableError:
            raise ValidationError(
                {
                    "career_id": [
                        "Selected career is not available."
                    ]
                }
            )

    def _enum_value(self, value):
        return getattr(
            value,
            "value",
            value,
        )

    def _decimal_value(self, value):
        if value is None:
            return None

        return str(value)


class RoadmapListView(LearningSuggestionListView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = self._get_profile(
            request.user
        )
        career_id = self._get_career_id(
            request
        )
        plan = self._generate_plan(
            student_profile_id=profile.id,
            career_id=career_id,
        )
        serializer = RoadmapStepSerializer(
            plan.roadmap_steps,
            many=True,
        )

        return Response(
            {
                "data": {
                    "career_id": plan.career_id,
                    "career_name": plan.career_name,
                    "score_status": self._enum_value(
                        plan
                        .readiness_result
                        .score_status
                    ),
                    "readiness_score": (
                        self._decimal_value(
                            plan
                            .readiness_result
                            .readiness_score
                        )
                    ),
                    "roadmap_steps": serializer.data,
                }
            }
        )
