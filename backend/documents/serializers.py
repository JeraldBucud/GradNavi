from rest_framework import serializers


class ResumeGenerationRequestSerializer(serializers.Serializer):
    """
    Resume generation accepts no client-supplied profile or prompt data.
    """

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected an object.")

        if data:
            raise serializers.ValidationError(
                {
                    field: "This field is not allowed."
                    for field in sorted(data)
                }
            )

        return {}


class ResumeDraftSerializer(serializers.Serializer):
    professional_summary = serializers.CharField()
    skills = serializers.ListField(
        child=serializers.CharField(),
    )
    education = serializers.ListField(
        child=serializers.CharField(),
    )
    experience = serializers.ListField(
        child=serializers.CharField(),
    )
    projects = serializers.ListField(
        child=serializers.CharField(),
    )
    missing_information = serializers.ListField(
        child=serializers.CharField(),
    )
    limitations = serializers.ListField(
        child=serializers.CharField(),
    )
    is_draft = serializers.BooleanField()
    requires_user_review = serializers.BooleanField()

