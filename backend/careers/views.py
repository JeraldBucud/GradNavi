from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from careers.serializers import (
    CareerSelectionQuerySerializer,
    CareerReadinessResultSerializer,
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

from ai_services.providers.openai_text import (
    OpenAITextProvider,
    resolve_text_model,
)

from careers.services.composite_recommendation import (
    COMPETENCY_WEIGHT,
    SEMANTIC_WEIGHT,
    TECHNOLOGY_WEIGHT,
    generate_composite_recommendations,
)
from careers.services.recommendation_cache import (
    SCORING_VERSION,
    build_recommendation_cache_key,
    get_valid_recommendation_snapshot,
    store_recommendation_snapshot,
)

from careers.services.recommendation_explanation import (
    EXPLANATION_VERSION,
    generate_top_match_explanation,
    select_top_recommendation,
)
from careers.services.readiness_scoring import (
    CareerNotAvailableError,
    CareerNotFoundError,
    calculate_selected_career_readiness,
)

from careers.services.skill_gap_summary import (
    SKILL_GAP_SUMMARY_VERSION,
    build_fix_first,
    build_skill_gap_summary_cache_key,
    build_skill_gap_summary_source,
    generate_skill_gap_summary,
    get_cached_skill_gap_summary,
    store_skill_gap_summary,
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

        cache_key = (
            build_recommendation_cache_key(
                student_profile=profile,
            )
        )

        snapshot = (
            get_valid_recommendation_snapshot(
                student_profile=profile,
                cache_key=cache_key,
            )
        )

        if snapshot is not None:
            return Response(
                {
                    "data": snapshot.payload,
                }
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

        payload = {
            "scoring_model": (
                SCORING_VERSION
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

        store_recommendation_snapshot(
            student_profile=profile,
            payload=payload,
            embedding_model=(
                report.model or ""
            ),
            prompt_tokens=(
                report.prompt_tokens
            ),
            total_tokens=(
                report.total_tokens
            ),
            career_count=(
                report.career_count
            ),
            cache_key=cache_key,
        )

        return Response(
            {
                "data": payload,
            }
        )

    def _get_profile(self, user):
        try:
            return StudentProfile.objects.get(
                user=user,
            )
        except StudentProfile.DoesNotExist:
            raise NotFound(
                "Student profile was not found."
            )



class RecommendationExplanationUnavailable(APIException):
    """
    Returned when the optional Top Match explanation cannot be generated.
    """

    status_code = 503

    default_detail = (
        "AI Career Match explanation is currently unavailable."
    )

    default_code = (
        "ai_explanation_unavailable"
    )


class RecommendationSnapshotUnavailable(APIException):
    """
    Returned when Career Recommendations must be generated first.
    """

    status_code = 409

    default_detail = (
        "Career Recommendations must be loaded before requesting "
        "a Top Match explanation."
    )

    default_code = (
        "recommendation_snapshot_unavailable"
    )


class TopMatchExplanationView(APIView):
    permission_classes = (
        IsAuthenticated,
    )

    def get(
        self,
        request,
    ):
        profile = self._get_profile(
            request.user
        )

        cache_key = (
            build_recommendation_cache_key(
                student_profile=(
                    profile
                ),
            )
        )

        snapshot = (
            get_valid_recommendation_snapshot(
                student_profile=(
                    profile
                ),
                cache_key=(
                    cache_key
                ),
            )
        )

        if snapshot is None:
            raise (
                RecommendationSnapshotUnavailable()
            )

        top_recommendation = (
            select_top_recommendation(
                snapshot.payload
            )
        )

        career_id = (
            top_recommendation.get(
                "career_id"
            )
        )

        expected_model = (
            resolve_text_model()
        )

        cached = (
            snapshot
            .payload
            .get(
                "top_match_explanation"
            )
        )

        if (
            isinstance(
                cached,
                dict,
            )
            and cached.get(
                "career_id"
            )
            == career_id
            and cached.get(
                "version"
            )
            == EXPLANATION_VERSION
            and cached.get(
                "model"
            )
            == expected_model
            and isinstance(
                cached.get(
                    "match_explanation"
                ),
                str,
            )
            and cached[
                "match_explanation"
            ].strip()
        ):
            return Response(
                {
                    "data": {
                        **cached,
                        "cached": True,
                    }
                }
            )

        try:
            provider = (
                OpenAITextProvider(
                    model=(
                        expected_model
                    )
                )
            )

            result = (
                generate_top_match_explanation(
                    recommendation=(
                        top_recommendation
                    ),
                    provider=(
                        provider
                    ),
                )
            )

        except AIProviderError as error:
            raise (
                RecommendationExplanationUnavailable()
            ) from error

        usage = getattr(
            provider,
            "last_usage",
            {},
        )

        explanation_payload = {
            "career_id": (
                career_id
            ),
            "match_explanation": (
                result.explanation
            ),
            "is_ai_generated": True,
            "model": (
                provider.model
            ),
            "version": (
                EXPLANATION_VERSION
            ),
            "usage": {
                "input_tokens": (
                    usage.get(
                        "input_tokens",
                        0,
                    )
                ),
                "output_tokens": (
                    usage.get(
                        "output_tokens",
                        0,
                    )
                ),
                "total_tokens": (
                    usage.get(
                        "total_tokens",
                        0,
                    )
                ),
            },
        }

        updated_payload = dict(
            snapshot.payload
        )

        updated_payload[
            "top_match_explanation"
        ] = (
            explanation_payload
        )

        snapshot.payload = (
            updated_payload
        )

        snapshot.save(
            update_fields=[
                "payload",
                "generated_at",
            ]
        )

        return Response(
            {
                "data": {
                    **explanation_payload,
                    "cached": False,
                }
            }
        )

    def _get_profile(
        self,
        user,
    ):
        try:
            return (
                StudentProfile
                .objects
                .get(
                    user=user,
                )
            )

        except StudentProfile.DoesNotExist:
            raise NotFound(
                "Student profile was not found."
            )


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


class SkillGapSummaryAIUnavailable(APIException):
    status_code = 503

    default_detail = (
        "AI Skill Gap Summary is currently unavailable."
    )

    default_code = (
        "ai_skill_gap_summary_unavailable"
    )


class SkillGapSummaryView(APIView):
    """
    Explain deterministic Skill Gap results with a cached
    AI-generated Student-facing summary.

    Scores, statuses, priorities, and Fix First values
    remain deterministic.
    """

    permission_classes = (
        IsAuthenticated,
    )


    def get(
        self,
        request,
    ):
        profile = self._get_profile(
            request.user
        )

        career_id = self._get_career_id(
            request
        )

        plan = self._generate_plan(
            student_profile_id=(
                profile.id
            ),
            career_id=career_id,
        )

        source = (
            build_skill_gap_summary_source(
                plan
            )
        )

        model = (
            resolve_text_model()
        )

        cache_key = (
            build_skill_gap_summary_cache_key(
                source,
                model=model,
            )
        )

        cached = (
            get_cached_skill_gap_summary(
                student_profile_id=(
                    profile.id
                ),
                career_id=career_id,
                cache_key=cache_key,
                model=model,
            )
        )

        if cached is not None:
            return Response(
                {
                    "data": {
                        **cached.payload,
                        "cached": True,
                    }
                }
            )

        try:
            provider = (
                OpenAITextProvider(
                    model=model
                )
            )

            result = (
                generate_skill_gap_summary(
                    source=source,
                    provider=provider,
                )
            )

        except AIProviderError as error:
            raise (
                SkillGapSummaryAIUnavailable()
            ) from error

        usage = getattr(
            provider,
            "last_usage",
            {},
        )

        payload = {
            "career_id": (
                plan.career_id
            ),
            "career_name": (
                plan.career_name
            ),
            "readiness_explanation": (
                result.readiness_explanation
            ),
            "fix_first": (
                build_fix_first(
                    plan
                )
            ),
            "recommended_next_steps": (
                list(
                    result
                    .recommended_next_steps
                )
            ),
            "is_ai_generated": True,
            "model": provider.model,
            "version": (
                SKILL_GAP_SUMMARY_VERSION
            ),
            "usage": {
                "input_tokens": (
                    usage.get(
                        "input_tokens",
                        0,
                    )
                ),
                "output_tokens": (
                    usage.get(
                        "output_tokens",
                        0,
                    )
                ),
                "total_tokens": (
                    usage.get(
                        "total_tokens",
                        0,
                    )
                ),
            },
        }

        store_skill_gap_summary(
            student_profile_id=(
                profile.id
            ),
            career_id=career_id,
            cache_key=cache_key,
            model=provider.model,
            payload=payload,
        )

        return Response(
            {
                "data": {
                    **payload,
                    "cached": False,
                }
            }
        )


    def _get_profile(
        self,
        user,
    ):
        try:
            return (
                StudentProfile
                .objects
                .get(
                    user=user,
                )
            )

        except StudentProfile.DoesNotExist:
            raise NotFound(
                "Student profile was not found."
            )


    def _get_career_id(
        self,
        request,
    ):
        serializer = (
            CareerSelectionQuerySerializer(
                data=request.query_params,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        return (
            serializer
            .validated_data[
                "career_id"
            ]
        )


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


class SelectedCareerReadinessView(APIView):
    """
    Expose the complete deterministic WBS 5.5
    selected-Career readiness result.

    This endpoint performs no AI generation.
    """

    permission_classes = (
        IsAuthenticated,
    )


    def get(
        self,
        request,
    ):
        profile = self._get_profile(
            request.user
        )

        career_id = self._get_career_id(
            request
        )

        result = self._calculate_readiness(
            student_profile_id=profile.id,
            career_id=career_id,
        )

        serializer = (
            CareerReadinessResultSerializer(
                result
            )
        )

        return Response(
            {
                "data": serializer.data,
            }
        )


    def _get_profile(
        self,
        user,
    ):
        try:
            return (
                StudentProfile.objects.get(
                    user=user,
                )
            )

        except StudentProfile.DoesNotExist:
            raise NotFound(
                "Student profile was not found."
            )


    def _get_career_id(
        self,
        request,
    ):
        serializer = (
            CareerSelectionQuerySerializer(
                data=request.query_params,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        return (
            serializer
            .validated_data[
                "career_id"
            ]
        )


    def _calculate_readiness(
        self,
        *,
        student_profile_id,
        career_id,
    ):
        try:
            return (
                calculate_selected_career_readiness(
                    student_profile_id=(
                        student_profile_id
                    ),
                    career_id=career_id,
                )
            )

        except CareerNotFoundError:
            raise NotFound(
                "Selected career was not found."
            )

        except CareerNotAvailableError:
            raise ValidationError(
                {
                    "career_id": [
                        (
                            "Selected career "
                            "is not available."
                        )
                    ]
                }
            )


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
