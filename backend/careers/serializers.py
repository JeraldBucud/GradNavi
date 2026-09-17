from rest_framework import serializers


class CareerSelectionQuerySerializer(serializers.Serializer):
    career_id = serializers.IntegerField(
        min_value=1,
        required=True,
    )


class RecommendationResultSerializer(serializers.Serializer):
    career_id = serializers.IntegerField()
    career_name = serializers.CharField()
    score_status = serializers.SerializerMethodField()
    recommendation_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True,
    )
    rank = serializers.IntegerField(
        allow_null=True,
    )
    matched_weight = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total_weight = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    matched_competencies = serializers.ListField(
        child=serializers.CharField(),
    )
    missing_competencies = serializers.ListField(
        child=serializers.CharField(),
    )
    matched_technologies = serializers.ListField(
        child=serializers.CharField(),
    )
    esco_essential_skills = serializers.ListField(
        child=serializers.CharField(),
    )
    esco_optional_skills = serializers.ListField(
        child=serializers.CharField(),
    )
    esco_essential_matches = serializers.IntegerField()
    esco_optional_matches = serializers.IntegerField()

    def get_score_status(self, result):
        return getattr(
            result.score_status,
            "value",
            result.score_status,
        )


class CompositeRecommendationResultSerializer(
    serializers.Serializer
):
    """
    API representation of the locked WBS 5.3
    composite Career Recommendation result.
    """

    career_id = serializers.IntegerField()

    career_name = serializers.CharField()

    recommendation_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    rank = serializers.IntegerField(
        allow_null=True,
    )


    competency_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True,
    )

    competency_normalized_score = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        allow_null=True,
    )

    competency_status = (
        serializers.SerializerMethodField()
    )


    technology_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True,
    )

    technology_normalized_score = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        allow_null=True,
    )

    technology_status = (
        serializers.SerializerMethodField()
    )

    technology_student_alignment_ratio = (
        serializers.DecimalField(
            max_digits=7,
            decimal_places=6,
            allow_null=True,
        )
    )

    technology_active = serializers.BooleanField()


    semantic_alignment_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    semantic_normalized_score = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
    )

    semantic_context_mode = (
        serializers.SerializerMethodField()
    )


    effective_competency_weight = (
        serializers.DecimalField(
            max_digits=7,
            decimal_places=6,
        )
    )

    effective_technology_weight = (
        serializers.DecimalField(
            max_digits=7,
            decimal_places=6,
        )
    )

    effective_semantic_weight = (
        serializers.DecimalField(
            max_digits=7,
            decimal_places=6,
        )
    )


    matched_competencies = (
        serializers.SerializerMethodField()
    )

    missing_competencies = (
        serializers.SerializerMethodField()
    )

    matched_technologies = (
        serializers.SerializerMethodField()
    )

    missing_technologies = (
        serializers.SerializerMethodField()
    )

    esco_essential_skills = (
        serializers.SerializerMethodField()
    )

    esco_optional_skills = (
        serializers.SerializerMethodField()
    )

    semantic_essential_esco_count = (
        serializers.SerializerMethodField()
    )


    def _enum_value(
        self,
        value,
    ):
        return getattr(
            value,
            "value",
            value,
        )


    def get_competency_status(
        self,
        result,
    ):
        return self._enum_value(
            result.competency_status
        )


    def get_technology_status(
        self,
        result,
    ):
        return self._enum_value(
            result.technology_status
        )


    def get_semantic_context_mode(
        self,
        result,
    ):
        return self._enum_value(
            result.semantic_context_mode
        )


    def get_matched_competencies(
        self,
        result,
    ):
        return list(
            result
            .competency_result
            .matched_competencies
        )


    def get_missing_competencies(
        self,
        result,
    ):
        return list(
            result
            .competency_result
            .missing_competencies
        )


    def get_matched_technologies(
        self,
        result,
    ):
        return list(
            result
            .technology_result
            .matched_technologies
        )


    def get_missing_technologies(
        self,
        result,
    ):
        return list(
            result
            .technology_result
            .missing_technologies
        )


    def get_esco_essential_skills(
        self,
        result,
    ):
        return list(
            result
            .competency_result
            .esco_essential_skills
        )


    def get_esco_optional_skills(
        self,
        result,
    ):
        return list(
            result
            .competency_result
            .esco_optional_skills
        )


    def get_semantic_essential_esco_count(
        self,
        result,
    ):
        return (
            result
            .semantic_result
            .essential_esco_count
        )



class LearningResourceSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    provider = serializers.CharField()
    url = serializers.URLField()
    resource_type = serializers.CharField()
    description = serializers.CharField()


class LearningSuggestionSerializer(serializers.Serializer):
    priority = serializers.IntegerField()
    skill_id = serializers.IntegerField()
    skill_name = serializers.CharField()
    gap_status = serializers.SerializerMethodField()
    current_proficiency = serializers.CharField(
        allow_null=True,
    )
    current_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    required_level = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    gap_amount = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    importance = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    resources = LearningResourceSummarySerializer(
        many=True,
    )

    def get_gap_status(self, suggestion):
        return getattr(
            suggestion.gap_status,
            "value",
            suggestion.gap_status,
        )


class RoadmapStepSerializer(serializers.Serializer):
    step_number = serializers.IntegerField()
    skill_id = serializers.IntegerField()
    skill_name = serializers.CharField()
    gap_status = serializers.SerializerMethodField()
    current_proficiency = serializers.CharField(
        allow_null=True,
    )
    current_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    required_level = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    gap_amount = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    importance = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    resources = LearningResourceSummarySerializer(
        many=True,
    )

    def get_gap_status(self, step):
        return getattr(
            step.gap_status,
            "value",
            step.gap_status,
        )
