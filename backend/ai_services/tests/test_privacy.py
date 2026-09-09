"""
Automated privacy tests for GradNavi WBS 6.2.

These tests verify the AI privacy allowlist and the conversion from
Django Student Profile data into StudentProfileContext.

The tests confirm approved career information enters AI context while
identity, authentication, unrelated profile data, internal IDs, and
project URLs stay outside the AI boundary.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from profiles.models import (
    CareerGoal,
    Education,
    Experience,
    Interest,
    PersonalityResponse,
    Project,
    Skill,
    StudentInterest,
    StudentProfile,
    StudentSkill,
)

from ai_services.safety.privacy import (
    AI_PROFILE_ALLOWLIST,
    build_student_profile_context,
)
from ai_services.schemas.common import StudentProfileContext


class AIProfilePrivacyTests(TestCase):
    """
    Tests for the WBS 6.2 Student Profile privacy boundary.
    """

    def setUp(self):
        """
        Create one Student Profile containing both approved and excluded data.

        Excluded data is intentionally populated so tests prove the privacy
        mapper does not forward it into StudentProfileContext.
        """

        User = get_user_model()

        self.user = User.objects.create_user(
            email="privacy-test@example.com",
            password="TemporaryPassword123!",
        )

        self.profile = StudentProfile.objects.create(
            user=self.user,
        )

        self.python_skill = Skill.objects.create(
            name="Python",
            concept_type=Skill.ConceptType.TECHNOLOGY,
            category="Programming",
            description="Internal canonical skill description.",
        )

        self.django_skill = Skill.objects.create(
            name="Django",
            concept_type=Skill.ConceptType.TECHNOLOGY,
            category="Framework",
            description="Internal framework description.",
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.python_skill,
            proficiency_level=StudentSkill.ProficiencyLevel.PROFICIENT,
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.django_skill,
            proficiency_level=StudentSkill.ProficiencyLevel.DEVELOPING,
        )

        Education.objects.create(
            student_profile=self.profile,
            institution_name="Example University",
            qualification="Master of Information Technology",
            field_of_study="Software Development",
            start_date=date(2025, 2, 1),
            end_date=date(2026, 11, 30),
            description="Postgraduate software-development study.",
        )

        Experience.objects.create(
            student_profile=self.profile,
            job_title="IT Specialist",
            company="Example Company",
            start_date=date(2024, 1, 1),
            end_date=None,
            is_current=True,
            description="Supported business technology systems.",
        )

        Project.objects.create(
            student_profile=self.profile,
            name="GradNavi",
            description="AI-assisted career guidance project.",
            project_url="https://private-project-url.example.com",
            start_date=date(2026, 7, 1),
            end_date=None,
        )

        CareerGoal.objects.create(
            student_profile=self.profile,
            target_role="Software Developer",
            description="Move into professional software development.",
        )

        self.interest = Interest.objects.create(
            name="Artificial Intelligence",
            category="Technology",
        )

        StudentInterest.objects.create(
            student_profile=self.profile,
            interest=self.interest,
        )

        PersonalityResponse.objects.create(
            student_profile=self.profile,
            question_key="private_personality_question",
            response_value="private-personality-response",
        )

    def test_privacy_allowlist_contains_only_approved_sections(self):
        expected = (
            "skills",
            "education",
            "experience",
            "projects",
            "career_goals",
        )

        self.assertEqual(
            AI_PROFILE_ALLOWLIST,
            expected,
        )

    def test_mapper_returns_student_profile_context(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        self.assertIsInstance(
            context,
            StudentProfileContext,
        )

    def test_approved_profile_information_is_included(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        self.assertEqual(
            len(context.skills),
            2,
        )

        self.assertEqual(
            context.education[0].institution_name,
            "Example University",
        )

        self.assertEqual(
            context.experience[0].job_title,
            "IT Specialist",
        )

        self.assertEqual(
            context.projects[0].name,
            "GradNavi",
        )

        self.assertEqual(
            context.career_goals[0].target_role,
            "Software Developer",
        )

    def test_account_identity_information_is_excluded(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        fields = set(context.model_fields)

        forbidden_fields = {
            "user",
            "user_id",
            "student_profile_id",
            "profile_id",
            "email",
            "role",
            "password",
            "first_name",
            "last_name",
        }

        self.assertTrue(
            forbidden_fields.isdisjoint(fields)
        )

    def test_email_value_does_not_leak_into_context(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        serialized = context.model_dump_json()

        self.assertNotIn(
            self.user.email,
            serialized,
        )

    def test_interests_are_excluded(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        serialized = context.model_dump_json()

        self.assertNotIn(
            self.interest.name,
            serialized,
        )

        self.assertNotIn(
            "interests",
            context.model_fields,
        )

    def test_personality_responses_are_excluded(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        serialized = context.model_dump_json()

        self.assertNotIn(
            "private_personality_question",
            serialized,
        )

        self.assertNotIn(
            "private-personality-response",
            serialized,
        )

        self.assertNotIn(
            "personality_responses",
            context.model_fields,
        )

    def test_project_url_is_excluded(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        serialized = context.model_dump_json()

        self.assertNotIn(
            "https://private-project-url.example.com",
            serialized,
        )

        project_fields = set(
            context.projects[0].model_fields
        )

        self.assertNotIn(
            "project_url",
            project_fields,
        )

    def test_skill_internal_metadata_is_excluded(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        skill_fields = set(
            context.skills[0].model_fields
        )

        forbidden_fields = {
            "id",
            "skill_id",
            "concept_type",
            "category",
            "description",
            "created_at",
            "updated_at",
        }

        self.assertTrue(
            forbidden_fields.isdisjoint(skill_fields)
        )

    def test_skills_are_ordered_by_name(self):
        context = build_student_profile_context(
            student_profile=self.profile,
        )

        names = [
            skill.name
            for skill in context.skills
        ]

        self.assertEqual(
            names,
            ["Django", "Python"],
        )

    def test_empty_student_profile_produces_valid_empty_context(self):
        User = get_user_model()

        user = User.objects.create_user(
            email="empty-profile@example.com",
            password="TemporaryPassword123!",
        )

        empty_profile = StudentProfile.objects.create(
            user=user,
        )

        context = build_student_profile_context(
            student_profile=empty_profile,
        )

        self.assertEqual(
            context.skills,
            [],
        )

        self.assertEqual(
            context.education,
            [],
        )

        self.assertEqual(
            context.experience,
            [],
        )

        self.assertEqual(
            context.projects,
            [],
        )

        self.assertEqual(
            context.career_goals,
            [],
        )