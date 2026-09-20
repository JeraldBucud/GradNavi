from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from careers.serializers import (
    CareerSelectionQuerySerializer,
    CareerReadinessResultSerializer,
    CompositeRecommendationResultSerializer,
    ExploreCareerItemSerializer,
    ExploreCareerQuerySerializer,
    LearningResourceFeedbackInputSerializer,
    LearningResourceRecommendationQuerySerializer,
    LearningResourceReportInputSerializer,
    LearningSuggestionSerializer,
    RoadmapProgressMutationSerializer,
    RoadmapStepSerializer,
)
from careers.services.explore_careers import (
    CareerEvaluationResultUnavailableError,
    CareerEvaluationSnapshotUnavailableError,
    ExploreCareerNotAvailableError,
    ExploreCareerNotFoundError,
    RECOMMENDED_CAREER_LIMIT,
    evaluate_career_from_snapshot,
    list_explore_career_categories,
    list_explore_careers,
    list_guidance_careers,
)

from careers.services.learning_roadmap import generate_learning_plan
from ai_services.exceptions import (
    AIMissingContextError,
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
from careers.services.learning_resource_discovery import (
    ensure_learning_resource_catalogue,
)
from careers.services.learning_resource_guidance import (
    get_or_generate_learning_resource_guidance,
)
from careers.services.learning_resource_interactions import (
    LearningResourceUnavailableError,
    load_student_feedback_by_resource,
    report_learning_resource,
    set_learning_resource_feedback,
)
from careers.services.learning_resource_recommendations import (
    load_ranked_learning_resources,
)
from careers.services.roadmap_guidance import (
    get_or_generate_roadmap_guidance,
)
from careers.services.roadmap_overview import (
    generate_roadmap_overview,
)
from careers.services.roadmap_progress import (
    RoadmapProgressTransitionError,
    RoadmapStepNotFoundError,
    complete_roadmap_step,
    reconcile_roadmap_progress,
    start_roadmap_step,
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



class RecommendationProfileIncomplete(APIException):
    """
    Returned when the student profile does not contain enough
    approved context to generate career recommendations.
    """

    status_code = 400

    default_detail = (
        "Complete your profile before generating "
        "career recommendations."
    )

    default_code = (
        "insufficient_profile_context"
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

        except AIMissingContextError as error:
            raise RecommendationProfileIncomplete() from error

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


class _UnavailableOptionalTextProvider:
    """
    Lets optional AI features fall back cleanly when
    the configured provider is unavailable.
    """

    def generate(
        self,
        *,
        prompt_package,
        output_model,
    ):
        raise AIProviderError(
            "Optional AI provider is unavailable."
        )


def _optional_text_provider(
    *,
    model,
):
    try:
        return OpenAITextProvider(
            model=model
        )

    except AIProviderError:
        return (
            _UnavailableOptionalTextProvider()
        )


def _student_profile_for_api(
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


def _enum_api_value(
    value,
):
    return getattr(
        value,
        "value",
        value,
    )


def _decimal_api_value(
    value,
):
    if value is None:
        return None

    return str(
        value
    )


def _datetime_api_value(
    value,
):
    if value is None:
        return None

    return value.isoformat()


def _learning_plan_for_api(
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
                    (
                        "Selected career "
                        "is not available."
                    )
                ]
            }
        )


def _roadmap_overview_for_api(
    *,
    student_profile_id,
    career_id,
):
    try:
        return (
            generate_roadmap_overview(
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


class RoadmapOverviewView(APIView):
    """
    Additive Sprint 3 Career Roadmap contract.

    Existing /roadmaps/ behaviour stays unchanged.
    """

    permission_classes = (
        IsAuthenticated,
    )


    def get(
        self,
        request,
    ):
        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        query = (
            CareerSelectionQuerySerializer(
                data=request.query_params,
            )
        )

        query.is_valid(
            raise_exception=True
        )

        career_id = (
            query
            .validated_data[
                "career_id"
            ]
        )

        overview = (
            _roadmap_overview_for_api(
                student_profile_id=(
                    profile.id
                ),
                career_id=career_id,
            )
        )

        model = (
            resolve_text_model()
        )

        guidance = (
            get_or_generate_roadmap_guidance(
                student_profile=profile,
                overview=overview,
                provider=(
                    _optional_text_provider(
                        model=model
                    )
                ),
                model=model,
            )
        )

        guidance_by_skill = {
            item[
                "skill_name"
            ]: item
            for item
            in guidance[
                "guidance_items"
            ]
        }

        steps = []

        for step in (
            overview.roadmap_steps
        ):
            personalised = (
                guidance_by_skill.get(
                    step.skill_name
                )
            )

            steps.append(
                {
                    "step_number": (
                        step.step_number
                    ),
                    "skill_id": (
                        step.skill_id
                    ),
                    "skill_name": (
                        step.skill_name
                    ),
                    "gap_status": (
                        _enum_api_value(
                            step.gap_status
                        )
                    ),
                    "current_proficiency": (
                        step.current_proficiency
                    ),
                    "current_score": (
                        _decimal_api_value(
                            step.current_score
                        )
                    ),
                    "required_level": (
                        _decimal_api_value(
                            step.required_level
                        )
                    ),
                    "gap_amount": (
                        _decimal_api_value(
                            step.gap_amount
                        )
                    ),
                    "importance": (
                        _decimal_api_value(
                            step.importance
                        )
                    ),
                    "progress_status": (
                        step.progress_status
                    ),
                    "started_at": (
                        _datetime_api_value(
                            step.started_at
                        )
                    ),
                    "completed_at": (
                        _datetime_api_value(
                            step.completed_at
                        )
                    ),
                    "why_this_matters": (
                        personalised[
                            "why_this_matters"
                        ]
                        if personalised
                        else None
                    ),
                    "your_focus": (
                        personalised[
                            "your_focus"
                        ]
                        if personalised
                        else None
                    ),
                    "resources": [
                        {
                            "id": resource.id,
                            "title": (
                                resource.title
                            ),
                            "provider": (
                                resource.provider
                            ),
                            "url": (
                                resource.url
                            ),
                            "resource_type": (
                                resource.resource_type
                            ),
                            "description": (
                                resource.description
                            ),
                        }
                        for resource
                        in step.resources
                    ],
                }
            )

        return Response(
            {
                "data": {
                    "career_id": (
                        overview.career_id
                    ),
                    "career_name": (
                        overview.career_name
                    ),
                    "score_status": (
                        _enum_api_value(
                            overview.score_status
                        )
                    ),
                    "readiness_score": (
                        _decimal_api_value(
                            overview.readiness_score
                        )
                    ),
                    "progress_summary": {
                        "total": (
                            overview
                            .progress_summary
                            .total
                        ),
                        "completed": (
                            overview
                            .progress_summary
                            .completed
                        ),
                        "in_progress": (
                            overview
                            .progress_summary
                            .in_progress
                        ),
                        "not_started": (
                            overview
                            .progress_summary
                            .not_started
                        ),
                    },
                    "guidance": {
                        "is_ai_generated": (
                            guidance[
                                "is_ai_generated"
                            ]
                        ),
                        "fallback": (
                            guidance[
                                "fallback"
                            ]
                        ),
                        "cached": (
                            guidance[
                                "cached"
                            ]
                        ),
                        "model": (
                            guidance[
                                "model"
                            ]
                        ),
                        "version": (
                            guidance[
                                "version"
                            ]
                        ),
                    },
                    "roadmap_steps": (
                        steps
                    ),
                }
            }
        )


class RoadmapProgressStartView(APIView):
    permission_classes = (
        IsAuthenticated,
    )


    def post(
        self,
        request,
    ):
        return self._mutate(
            request=request,
            operation="start",
        )


    def _mutate(
        self,
        *,
        request,
        operation,
    ):
        serializer = (
            RoadmapProgressMutationSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        career_id = (
            serializer
            .validated_data[
                "career_id"
            ]
        )

        skill_id = (
            serializer
            .validated_data[
                "skill_id"
            ]
        )

        plan = (
            _learning_plan_for_api(
                student_profile_id=(
                    profile.id
                ),
                career_id=career_id,
            )
        )

        try:
            step = (
                start_roadmap_step(
                    plan=plan,
                    skill_id=skill_id,
                )
            )

        except RoadmapStepNotFoundError as error:
            raise ValidationError(
                {
                    "skill_id": [
                        str(
                            error
                        )
                    ]
                }
            )

        except (
            RoadmapProgressTransitionError
        ) as error:
            raise ValidationError(
                {
                    "status": [
                        str(
                            error
                        )
                    ]
                }
            )

        snapshot = (
            reconcile_roadmap_progress(
                plan=plan
            )
        )

        return Response(
            {
                "data": {
                    "career_id": (
                        career_id
                    ),
                    "skill_id": (
                        step.skill_id
                    ),
                    "status": (
                        step.status
                    ),
                    "started_at": (
                        _datetime_api_value(
                            step.started_at
                        )
                    ),
                    "completed_at": (
                        _datetime_api_value(
                            step.completed_at
                        )
                    ),
                    "progress_summary": {
                        "total": (
                            snapshot
                            .summary
                            .total
                        ),
                        "completed": (
                            snapshot
                            .summary
                            .completed
                        ),
                        "in_progress": (
                            snapshot
                            .summary
                            .in_progress
                        ),
                        "not_started": (
                            snapshot
                            .summary
                            .not_started
                        ),
                    },
                }
            }
        )


class RoadmapProgressCompleteView(
    RoadmapProgressStartView
):
    permission_classes = (
        IsAuthenticated,
    )


    def post(
        self,
        request,
    ):
        serializer = (
            RoadmapProgressMutationSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        career_id = (
            serializer
            .validated_data[
                "career_id"
            ]
        )

        skill_id = (
            serializer
            .validated_data[
                "skill_id"
            ]
        )

        plan = (
            _learning_plan_for_api(
                student_profile_id=(
                    profile.id
                ),
                career_id=career_id,
            )
        )

        try:
            step = (
                complete_roadmap_step(
                    plan=plan,
                    skill_id=skill_id,
                )
            )

        except RoadmapStepNotFoundError as error:
            raise ValidationError(
                {
                    "skill_id": [
                        str(
                            error
                        )
                    ]
                }
            )

        snapshot = (
            reconcile_roadmap_progress(
                plan=plan
            )
        )

        return Response(
            {
                "data": {
                    "career_id": (
                        career_id
                    ),
                    "skill_id": (
                        step.skill_id
                    ),
                    "status": (
                        step.status
                    ),
                    "started_at": (
                        _datetime_api_value(
                            step.started_at
                        )
                    ),
                    "completed_at": (
                        _datetime_api_value(
                            step.completed_at
                        )
                    ),
                    "progress_summary": {
                        "total": (
                            snapshot
                            .summary
                            .total
                        ),
                        "completed": (
                            snapshot
                            .summary
                            .completed
                        ),
                        "in_progress": (
                            snapshot
                            .summary
                            .in_progress
                        ),
                        "not_started": (
                            snapshot
                            .summary
                            .not_started
                        ),
                    },
                }
            }
        )


class LearningResourceRecommendationView(
    APIView
):
    """
    Ranked Sprint 3 Learning Resource contract.

    Existing /learning-resources/ behaviour stays unchanged.
    """

    permission_classes = (
        IsAuthenticated,
    )


    def get(
        self,
        request,
    ):
        serializer = (
            LearningResourceRecommendationQuerySerializer(
                data=request.query_params,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        career_id = (
            serializer
            .validated_data[
                "career_id"
            ]
        )

        skill_id = (
            serializer
            .validated_data[
                "skill_id"
            ]
        )

        access_type = (
            serializer
            .validated_data
            .get(
                "access_type"
            )
        )

        plan = (
            _learning_plan_for_api(
                student_profile_id=(
                    profile.id
                ),
                career_id=career_id,
            )
        )

        suggestion = next(
            (
                item
                for item
                in plan.suggestions
                if item.skill_id
                == skill_id
            ),
            None,
        )

        if suggestion is None:
            raise ValidationError(
                {
                    "skill_id": [
                        (
                            "Selected Skill is not "
                            "an unresolved gap for "
                            "this Career."
                        )
                    ]
                }
            )

        discovery = (
            ensure_learning_resource_catalogue(
                skill_id=skill_id,
            )
        )

        ranked = (
            load_ranked_learning_resources(
                skill_id=skill_id,
                skill_name=(
                    suggestion.skill_name
                ),
                career_name=(
                    plan.career_name
                ),
                access_types=(
                    (
                        access_type,
                    )
                    if access_type
                    else None
                ),
                limit=12,
            )
        )

        model = (
            resolve_text_model()
        )

        guidance = (
            get_or_generate_learning_resource_guidance(
                student_profile=profile,
                career_id=(
                    plan.career_id
                ),
                career_name=(
                    plan.career_name
                ),
                skill_id=skill_id,
                skill_name=(
                    suggestion.skill_name
                ),
                ranked_resources=(
                    ranked
                ),
                provider=(
                    _optional_text_provider(
                        model=model
                    )
                ),
                model=model,
            )
        )

        guidance_by_resource = {
            item[
                "resource_id"
            ]: item
            for item
            in guidance[
                "guidance_items"
            ]
        }

        feedback_by_resource = (
            load_student_feedback_by_resource(
                student_profile_id=(
                    profile.id
                ),
                resource_ids=(
                    resource.id
                    for resource
                    in ranked
                ),
            )
        )

        resources = []

        for index, resource in enumerate(
            ranked,
            start=1,
        ):
            personalised = (
                guidance_by_resource.get(
                    resource.id
                )
            )

            uses_ai = (
                index <= 6
                and personalised
                is not None
                and guidance[
                    "is_ai_generated"
                ]
            )

            resources.append(
                {
                    "rank": index,
                    "id": resource.id,
                    "title": (
                        resource.title
                    ),
                    "provider": (
                        resource.provider
                    ),
                    "url": (
                        resource.url
                    ),
                    "resource_type": (
                        resource.resource_type
                    ),
                    "access_type": (
                        resource.access_type
                    ),
                    "source_type": (
                        resource.source_type
                    ),
                    "health_status": (
                        resource.health_status
                    ),
                    "description": (
                        resource.description
                    ),
                    "last_checked_at": (
                        _datetime_api_value(
                            resource
                            .last_checked_at
                        )
                    ),
                    "last_verified_at": (
                        _datetime_api_value(
                            resource
                            .last_verified_at
                        )
                    ),
                    "helpful_count": (
                        resource.helpful_count
                    ),
                    "not_helpful_count": (
                        resource
                        .not_helpful_count
                    ),
                    "feedback_score": (
                        resource.feedback_score
                    ),
                    "student_feedback": (
                        feedback_by_resource
                        .get(
                            resource.id
                        )
                    ),
                    "why_this_fits": (
                        personalised[
                            "why_this_fits"
                        ]
                        if personalised
                        is not None
                        else (
                            resource
                            .why_this_fits
                        )
                    ),
                    "explanation_source": (
                        "ai"
                        if uses_ai
                        else "deterministic"
                    ),
                }
            )

        return Response(
            {
                "data": {
                    "career_id": (
                        plan.career_id
                    ),
                    "career_name": (
                        plan.career_name
                    ),
                    "score_status": (
                        _enum_api_value(
                            plan
                            .readiness_result
                            .score_status
                        )
                    ),
                    "readiness_score": (
                        _decimal_api_value(
                            plan
                            .readiness_result
                            .readiness_score
                        )
                    ),
                    "skill": {
                        "skill_id": (
                            suggestion.skill_id
                        ),
                        "skill_name": (
                            suggestion.skill_name
                        ),
                        "gap_status": (
                            _enum_api_value(
                                suggestion
                                .gap_status
                            )
                        ),
                        "current_proficiency": (
                            suggestion
                            .current_proficiency
                        ),
                        "current_score": (
                            _decimal_api_value(
                                suggestion
                                .current_score
                            )
                        ),
                        "required_level": (
                            _decimal_api_value(
                                suggestion
                                .required_level
                            )
                        ),
                        "gap_amount": (
                            _decimal_api_value(
                                suggestion
                                .gap_amount
                            )
                        ),
                    },
                    "discovery": {
                        "attempted": (
                            discovery
                            .attempted
                        ),
                        "reason": (
                            discovery
                            .reason
                        ),
                        "status": (
                            discovery
                            .status
                        ),
                        "resource_count_before": (
                            discovery
                            .resource_count_before
                        ),
                        "resource_count_after": (
                            discovery
                            .resource_count_after
                        ),
                        "requested_count": (
                            discovery
                            .requested_count
                        ),
                        "candidate_count": (
                            discovery
                            .candidate_count
                        ),
                        "persisted_count": (
                            discovery
                            .persisted_count
                        ),
                        "next_eligible_at": (
                            _datetime_api_value(
                                discovery
                                .next_eligible_at
                            )
                        ),
                    },
                    "resource_count": (
                        len(
                            resources
                        )
                    ),
                    "initial_visible_count": (
                        min(
                            6,
                            len(
                                resources
                            ),
                        )
                    ),
                    "maximum_resource_count": 12,
                    "guidance": {
                        "is_ai_generated": (
                            guidance[
                                "is_ai_generated"
                            ]
                        ),
                        "fallback": (
                            guidance[
                                "fallback"
                            ]
                        ),
                        "cached": (
                            guidance[
                                "cached"
                            ]
                        ),
                        "model": (
                            guidance[
                                "model"
                            ]
                        ),
                        "version": (
                            guidance[
                                "version"
                            ]
                        ),
                    },
                    "resources": (
                        resources
                    ),
                }
            }
        )


class LearningResourceFeedbackView(
    APIView
):
    permission_classes = (
        IsAuthenticated,
    )


    def put(
        self,
        request,
        resource_id,
    ):
        serializer = (
            LearningResourceFeedbackInputSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        try:
            result = (
                set_learning_resource_feedback(
                    student_profile=(
                        profile
                    ),
                    resource_id=(
                        resource_id
                    ),
                    feedback_type=(
                        serializer
                        .validated_data[
                            "feedback_type"
                        ]
                    ),
                )
            )

        except LearningResourceUnavailableError:
            raise NotFound(
                "Learning Resource was not found."
            )

        return Response(
            {
                "data": {
                    "resource_id": (
                        result.resource_id
                    ),
                    "feedback_type": (
                        result.feedback_type
                    ),
                    "helpful_count": (
                        result.helpful_count
                    ),
                    "not_helpful_count": (
                        result
                        .not_helpful_count
                    ),
                }
            }
        )


class LearningResourceReportCreateView(
    APIView
):
    permission_classes = (
        IsAuthenticated,
    )


    def post(
        self,
        request,
    ):
        serializer = (
            LearningResourceReportInputSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        try:
            result = (
                report_learning_resource(
                    student_profile=(
                        profile
                    ),
                    resource_id=(
                        serializer
                        .validated_data[
                            "resource_id"
                        ]
                    ),
                    reason=(
                        serializer
                        .validated_data[
                            "reason"
                        ]
                    ),
                    comment=(
                        serializer
                        .validated_data
                        .get(
                            "comment",
                            "",
                        )
                    ),
                )
            )

        except LearningResourceUnavailableError:
            raise NotFound(
                "Learning Resource was not found."
            )

        return Response(
            {
                "data": {
                    "report_id": (
                        result.report_id
                    ),
                    "resource_id": (
                        result.resource_id
                    ),
                    "reason": (
                        result.reason
                    ),
                    "status": (
                        result.status
                    ),
                    "created": (
                        result.created
                    ),
                }
            },
            status=(
                201
                if result.created
                else 200
            ),
        )


def _ensure_explore_recommendation_snapshot(
    student_profile,
):
    """
    Return the current RecommendationSnapshot.

    Existing Career Recommendations behaviour stays
    unchanged.

    If the Student Profile or reference-data state
    changed, Explore Careers refreshes the recommendation
    snapshot before continuing.
    """

    cache_key = (
        build_recommendation_cache_key(
            student_profile=(
                student_profile
            ),
        )
    )

    snapshot = (
        get_valid_recommendation_snapshot(
            student_profile=(
                student_profile
            ),
            cache_key=cache_key,
        )
    )

    if snapshot is not None:
        return (
            snapshot,
            False,
        )

    try:
        embedding_provider = (
            OpenAIEmbeddingProvider()
        )

        report = (
            generate_composite_recommendations(
                student_profile_id=(
                    student_profile.id
                ),
                embedding_provider=(
                    embedding_provider
                ),
            )
        )

    except AIProviderError as error:
        raise (
            RecommendationAIUnavailable()
        ) from error

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

    snapshot = (
        store_recommendation_snapshot(
            student_profile=(
                student_profile
            ),
            payload=payload,
            embedding_model=(
                report.model
                or ""
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
    )

    return (
        snapshot,
        True,
    )


def _explore_career_item_for_api(
    *,
    student_profile,
    career_id,
):
    items = (
        list_explore_careers(
            student_profile=(
                student_profile
            ),
        )
    )

    for item in items:
        if (
            item.career_id
            == career_id
        ):
            return item

    raise NotFound(
        "Career was not found."
    )


class ExploreCareerListView(APIView):
    permission_classes = (
        IsAuthenticated,
    )


    def get(
        self,
        request,
    ):
        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        query = (
            ExploreCareerQuerySerializer(
                data=request.query_params,
            )
        )

        query.is_valid(
            raise_exception=True,
        )

        _ensure_explore_recommendation_snapshot(
            profile
        )

        values = (
            query.validated_data
        )

        items = list(
            list_explore_careers(
                student_profile=profile,
                search=values[
                    "search"
                ],
                category=values[
                    "category"
                ],
                status=values[
                    "status"
                ],
            )
        )

        page = values[
            "page"
        ]

        page_size = values[
            "page_size"
        ]

        total_count = len(
            items
        )

        if total_count:
            total_pages = (
                (
                    total_count
                    + page_size
                    - 1
                )
                // page_size
            )
        else:
            total_pages = 0

        start = (
            (page - 1)
            * page_size
        )

        end = (
            start
            + page_size
        )

        page_items = (
            items[
                start:end
            ]
        )

        serializer = (
            ExploreCareerItemSerializer(
                page_items,
                many=True,
            )
        )

        categories = (
            list_explore_career_categories()
        )

        return Response(
            {
                "data": {
                    "results": (
                        serializer.data
                    ),
                    "pagination": {
                        "page": page,
                        "page_size": (
                            page_size
                        ),
                        "total_count": (
                            total_count
                        ),
                        "total_pages": (
                            total_pages
                        ),
                        "has_previous": (
                            page > 1
                        ),
                        "has_next": (
                            page
                            < total_pages
                        ),
                    },
                    "filters": {
                        "search": (
                            values[
                                "search"
                            ]
                        ),
                        "category": (
                            values[
                                "category"
                            ]
                        ),
                        "status": (
                            values[
                                "status"
                            ]
                        ),
                        "categories": list(
                            categories
                        ),
                    },
                    "recommended_limit": (
                        RECOMMENDED_CAREER_LIMIT
                    ),
                }
            }
        )


class ExploreCareerDetailView(APIView):
    permission_classes = (
        IsAuthenticated,
    )


    def get(
        self,
        request,
        career_id,
    ):
        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        _ensure_explore_recommendation_snapshot(
            profile
        )

        item = (
            _explore_career_item_for_api(
                student_profile=profile,
                career_id=career_id,
            )
        )

        serializer = (
            ExploreCareerItemSerializer(
                item
            )
        )

        return Response(
            {
                "data": (
                    serializer.data
                )
            }
        )


class ExploreCareerEvaluateView(APIView):
    permission_classes = (
        IsAuthenticated,
    )


    def post(
        self,
        request,
        career_id,
    ):
        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        (
            _snapshot,
            refreshed,
        ) = (
            _ensure_explore_recommendation_snapshot(
                profile
            )
        )

        try:
            evaluation = (
                evaluate_career_from_snapshot(
                    student_profile=profile,
                    career_id=career_id,
                )
            )

        except ExploreCareerNotFoundError:
            raise NotFound(
                "Career was not found."
            )

        except ExploreCareerNotAvailableError:
            raise ValidationError(
                {
                    "career_id": [
                        (
                            "Career is "
                            "not available."
                        )
                    ]
                }
            )

        except (
            CareerEvaluationSnapshotUnavailableError,
            CareerEvaluationResultUnavailableError,
        ):
            raise ValidationError(
                {
                    "career_id": [
                        (
                            "Career evaluation is "
                            "currently unavailable."
                        )
                    ]
                }
            )

        item = (
            _explore_career_item_for_api(
                student_profile=profile,
                career_id=career_id,
            )
        )

        serializer = (
            ExploreCareerItemSerializer(
                item
            )
        )

        return Response(
            {
                "data": {
                    "career": (
                        serializer.data
                    ),
                    "evaluation": (
                        evaluation.payload
                    ),
                    "recommendation_refreshed": (
                        refreshed
                    ),
                }
            }
        )


class GuidanceCareerListView(APIView):
    permission_classes = (
        IsAuthenticated,
    )


    def get(
        self,
        request,
    ):
        profile = (
            _student_profile_for_api(
                request.user
            )
        )

        _ensure_explore_recommendation_snapshot(
            profile
        )

        items = (
            list_guidance_careers(
                student_profile=profile,
            )
        )

        serializer = (
            ExploreCareerItemSerializer(
                items,
                many=True,
            )
        )

        return Response(
            {
                "data": {
                    "careers": (
                        serializer.data
                    ),
                    "recommended_limit": (
                        RECOMMENDED_CAREER_LIMIT
                    ),
                }
            }
        )
