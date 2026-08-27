from rest_framework import serializers

from .models import (
    CareerGoal,
    Education,
    Experience,
    Interest,
    PersonalityResponse,
    Project,
    StudentInterest,
    StudentProfile,
    StudentSkill,
)


class StudentSkillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="skill.id", read_only=True)
    name = serializers.CharField(source="skill.name", read_only=True)
    category = serializers.CharField(source="skill.category", read_only=True)

    class Meta:
        model = StudentSkill
        fields = ("id", "name", "category", "proficiency_level")
        read_only_fields = fields


class StudentInterestSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="interest.id", read_only=True)
    name = serializers.CharField(source="interest.name", read_only=True)
    category = serializers.CharField(source="interest.category", read_only=True)

    class Meta:
        model = StudentInterest
        fields = ("id", "name", "category")
        read_only_fields = fields


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            "id",
            "institution_name",
            "qualification",
            "field_of_study",
            "start_date",
            "end_date",
            "description",
        )
        read_only_fields = fields


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = (
            "id",
            "job_title",
            "company",
            "start_date",
            "end_date",
            "is_current",
            "description",
        )
        read_only_fields = fields


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "description",
            "project_url",
            "start_date",
            "end_date",
        )
        read_only_fields = fields


class CareerGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerGoal
        fields = ("id", "target_role", "description")
        read_only_fields = fields


class PersonalityResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalityResponse
        fields = ("id", "question_key", "response_value")
        read_only_fields = fields


class StudentProfileSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    career_goals = serializers.SerializerMethodField()
    personality_responses = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = (
            "skills",
            "interests",
            "education",
            "experience",
            "projects",
            "career_goals",
            "personality_responses",
        )
        read_only_fields = fields

    def get_skills(self, profile):
        student_skills = profile.student_skills.select_related("skill").order_by("id")
        return StudentSkillSerializer(student_skills, many=True).data

    def get_interests(self, profile):
        student_interests = profile.student_interests.select_related("interest").order_by("id")
        return StudentInterestSerializer(student_interests, many=True).data

    def get_education(self, profile):
        return EducationSerializer(profile.education.order_by("id"), many=True).data

    def get_experience(self, profile):
        return ExperienceSerializer(profile.experience.order_by("id"), many=True).data

    def get_projects(self, profile):
        return ProjectSerializer(profile.projects.order_by("id"), many=True).data

    def get_career_goals(self, profile):
        return CareerGoalSerializer(profile.career_goals.order_by("id"), many=True).data

    def get_personality_responses(self, profile):
        return PersonalityResponseSerializer(
            profile.personality_responses.order_by("id"),
            many=True,
        ).data
