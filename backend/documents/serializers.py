from rest_framework import serializers

from ai_services.schemas.common import SHORT_TEXT_MAX_LENGTH
from ai_services.schemas.inputs import JOB_DESCRIPTION_MAX_LENGTH


RESUME_FOCUS_CHOICES = (
    "balanced",
    "technical_skills",
    "professional_experience",
    "projects",
    "transferable_skills",
)

COVER_LETTER_TONE_CHOICES = (
    "professional",
    "warm",
    "technical",
    "concise",
)

COVER_LETTER_FOCUS_CHOICES = (
    "balanced",
    "skills_match",
    "experience",
    "projects",
    "career_transition",
)


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


class ResumeGenerationRequestSerializer(
    RejectUnknownFieldsMixin,
    serializers.Serializer,
):
    """
    Resume generation requires one authorized target Career.

    Student Profile data is resolved from the authenticated account.
    """

    target_career_id = serializers.IntegerField(
        min_value=1,
    )

    resume_focus = serializers.ChoiceField(
        choices=RESUME_FOCUS_CHOICES,
        default="balanced",
    )

    job_description = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=JOB_DESCRIPTION_MAX_LENGTH,
        trim_whitespace=True,
    )


class CoverLetterGenerationRequestSerializer(
    RejectUnknownFieldsMixin,
    serializers.Serializer,
):
    target_career_id = serializers.IntegerField(
        min_value=1,
    )

    tone = serializers.ChoiceField(
        choices=COVER_LETTER_TONE_CHOICES,
        default="professional",
    )

    cover_letter_focus = serializers.ChoiceField(
        choices=COVER_LETTER_FOCUS_CHOICES,
        default="balanced",
    )

    job_title = serializers.CharField(
        allow_blank=False,
        max_length=SHORT_TEXT_MAX_LENGTH,
        trim_whitespace=True,
    )

    company = serializers.CharField(
        allow_blank=False,
        max_length=SHORT_TEXT_MAX_LENGTH,
        trim_whitespace=True,
    )

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
