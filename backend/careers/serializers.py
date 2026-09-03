from rest_framework import serializers


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
