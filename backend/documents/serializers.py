from rest_framework import serializers

from ai_services.schemas.inputs import JOB_DESCRIPTION_MAX_LENGTH


class RejectUnknownFieldsMixin:
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Expected an object.")

        unknown_fields = set(data) - set(self.fields)
        if unknown_fields:
            raise serializers.ValidationError(
                {
                    field: "This field is not allowed."
                    for field in sorted(unknown_fields)
                }
            )

        return super().to_internal_value(data)


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


class CoverLetterGenerationRequestSerializer(
    RejectUnknownFieldsMixin,
    serializers.Serializer,
):
    job_description = serializers.CharField(
        allow_blank=False,
        max_length=JOB_DESCRIPTION_MAX_LENGTH,
        trim_whitespace=True,
    )


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


class CoverLetterDraftSerializer(serializers.Serializer):
    opening = serializers.CharField()
    body_paragraphs = serializers.ListField(
        child=serializers.CharField(),
    )
    closing = serializers.CharField()
    matched_profile_facts = serializers.ListField(
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

