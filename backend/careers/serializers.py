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
