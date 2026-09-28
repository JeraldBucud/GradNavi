from rest_framework import serializers

from accounts.models import User
from careers.models import (
    Career,
    LearningResource,
    LearningResourceReport,
)
from profiles.models import Skill


class AdminUserSerializer(serializers.ModelSerializer):
    """
    Safe administrative representation of a GradNavi user.

    Passwords and Student Profile data are intentionally excluded.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "date_joined",
            "last_login",
        )
        read_only_fields = (
            "id",
            "email",
            "role",
            "is_active",
            "date_joined",
            "last_login",
        )


class AdminCareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = (
            "id",
            "name",
            "description",
            "category",
            "active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AdminSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = (
            "id",
            "name",
            "concept_type",
            "category",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AdminLearningResourceSerializer(
    serializers.ModelSerializer
):
    skill_ids = serializers.PrimaryKeyRelatedField(
        source="skills",
        queryset=Skill.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = LearningResource
        fields = (
            "id",
            "title",
            "resource_key",
            "provider",
            "url",
            "resource_type",
            "description",
            "is_active",
            "access_type",
            "source_type",
            "health_status",
            "last_checked_at",
            "last_verified_at",
            "skill_ids",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AdminLearningResourceReportSerializer(
    serializers.ModelSerializer
):
    """
    Administrative review representation of a student-submitted
    learning-resource report.

    Only the review status may be changed by an administrator.
    """

    class Meta:
        model = LearningResourceReport
        fields = (
            "id",
            "student_profile",
            "learning_resource",
            "reason",
            "comment",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "student_profile",
            "learning_resource",
            "reason",
            "comment",
            "created_at",
            "updated_at",
        )