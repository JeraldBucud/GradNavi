"""
REST API serializers for GradNavi interview preparation.

WBS 6.6 exposes two interview operations:

1. Interview question generation
2. Interview answer feedback

The HTTP contracts mirror the validated WBS 6.2 AI contracts.
"""

from rest_framework import serializers

from ai_services.schemas.common import SHORT_TEXT_MAX_LENGTH
from ai_services.schemas.inputs import (
    DEFAULT_INTERVIEW_QUESTION_COUNT,
    INTERVIEW_QUESTION_MAX_LENGTH,
    JOB_DESCRIPTION_MAX_LENGTH,
    MAX_INTERVIEW_QUESTION_COUNT,
    MIN_INTERVIEW_QUESTION_COUNT,
    STUDENT_ANSWER_MAX_LENGTH,
)


class StrictCharField(serializers.CharField):
    """
    Reject non-string JSON values before DRF performs type conversion.

    WBS 6.2 AI contracts use strict Pydantic validation, so the REST
    boundary should not silently convert numbers or booleans into text.
    """

    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail("invalid")

        return super().to_internal_value(data)


class StrictIntegerField(serializers.IntegerField):
    """
    Reject non-integer JSON values before DRF performs type conversion.

    bool requires an explicit rejection because Python bool is a subclass
    of int.
    """

    def to_internal_value(self, data):
        if isinstance(data, bool) or not isinstance(data, int):
            self.fail("invalid")

        return super().to_internal_value(data)


class InterviewQuestionRequestSerializer(serializers.Serializer):
    """
    Validate an interview-question generation HTTP request.

    Full Student Profile information is intentionally excluded.
    """

    target_role = StrictCharField(
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    job_description = StrictCharField(
        required=False,
        allow_null=True,
        max_length=JOB_DESCRIPTION_MAX_LENGTH,
    )

    question_count = StrictIntegerField(
        required=False,
        default=DEFAULT_INTERVIEW_QUESTION_COUNT,
        min_value=MIN_INTERVIEW_QUESTION_COUNT,
        max_value=MAX_INTERVIEW_QUESTION_COUNT,
    )


class InterviewFeedbackRequestSerializer(serializers.Serializer):
    """
    Validate an interview-answer feedback HTTP request.

    The request contains only the information required by the
    WBS 6.2 InterviewFeedbackInput contract.
    """

    target_role = StrictCharField(
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    question = StrictCharField(
        max_length=INTERVIEW_QUESTION_MAX_LENGTH,
    )

    student_answer = StrictCharField(
        max_length=STUDENT_ANSWER_MAX_LENGTH,
    )


class InterviewQuestionSerializer(serializers.Serializer):
    """
    Serialize one validated generated interview question.
    """

    question = serializers.CharField()
    focus_area = serializers.CharField()


class InterviewQuestionSetSerializer(serializers.Serializer):
    """
    Serialize validated InterviewQuestionSet output.
    """

    questions = InterviewQuestionSerializer(
        many=True,
    )

    focus_areas = serializers.ListField(
        child=serializers.CharField(),
    )

    limitations = serializers.ListField(
        child=serializers.CharField(),
    )

    is_ai_generated = serializers.BooleanField()

    requires_user_review = serializers.BooleanField()


class InterviewFeedbackSerializer(serializers.Serializer):
    """
    Serialize validated InterviewFeedback output.
    """

    strengths = serializers.ListField(
        child=serializers.CharField(),
    )

    improvements = serializers.ListField(
        child=serializers.CharField(),
    )

    suggested_response = serializers.CharField()

    feedback_summary = serializers.CharField()

    limitations = serializers.ListField(
        child=serializers.CharField(),
    )

    is_ai_generated = serializers.BooleanField()

    requires_user_review = serializers.BooleanField()