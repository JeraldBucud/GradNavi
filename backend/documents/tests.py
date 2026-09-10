from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ai_services.exceptions import AIProviderTimeoutError
from ai_services.prompts.common import AIOperation, PromptPackage
from ai_services.safety.privacy import build_student_profile_context
from ai_services.schemas.outputs import ResumeDraft
from documents.services.resume_generation import generate_resume_draft
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


class FakeResumeProvider:
    def __init__(
        self,
        *,
        response: ResumeDraft | None = None,
        error: Exception | None = None,
    ):
        self.response = response or ResumeDraft(
            professional_summary="Backend student with Python experience.",
            skills=["Python", "Django"],
            education=["Master of Information Technology"],
            experience=["IT Specialist at Example Company"],
            projects=["GradNavi"],
            missing_information=[],
            limitations=["Draft content requires student review."],
            is_draft=True,
            requires_user_review=True,
        )
        self.error = error
        self.calls = []

    def generate(
        self,
        *,
        prompt_package: PromptPackage,
        output_model,
    ):
        self.calls.append(
            {
                "prompt_package": prompt_package,
                "output_model": output_model,
            }
        )

        if self.error is not None:
            raise self.error

        return self.response


class ResumeGenerationServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            email="resume-private@example.com",
            password="TemporaryPassword123!",
            first_name="Private",
            last_name="Student",
        )

        self.profile = StudentProfile.objects.create(
            user=self.user,
        )

        skill = Skill.objects.create(
            name="Python",
            concept_type=Skill.ConceptType.TECHNOLOGY,
            category="Programming",
            description="Internal skill metadata.",
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=StudentSkill.ProficiencyLevel.PROFICIENT,
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
            project_url="https://private-project.example.com",
            start_date=date(2026, 7, 1),
            end_date=None,
        )

        CareerGoal.objects.create(
            student_profile=self.profile,
            target_role="Software Developer",
            description="Move into professional software development.",
        )

        interest = Interest.objects.create(
            name="Private Interest",
            category="Private Category",
        )

        StudentInterest.objects.create(
            student_profile=self.profile,
            interest=interest,
        )

        PersonalityResponse.objects.create(
            student_profile=self.profile,
            question_key="private_personality_question",
            response_value="private-personality-response",
        )

    def test_approved_profile_context_reaches_provider_through_privacy_mapper(self):
        provider = FakeResumeProvider()

        with patch(
            "documents.services.resume_generation.build_student_profile_context",
            wraps=build_student_profile_context,
        ) as mapper:
            generate_resume_draft(
                student_profile=self.profile,
                ai_provider=provider,
            )

        mapper.assert_called_once_with(
            student_profile=self.profile,
        )

        self.assertEqual(
            len(provider.calls),
            1,
        )

        prompt_package = provider.calls[0]["prompt_package"]

        self.assertEqual(
            prompt_package.operation,
            AIOperation.RESUME_GENERATION,
        )
        self.assertIn(
            "Python",
            prompt_package.trusted_context,
        )
        self.assertIn(
            "Example University",
            prompt_package.trusted_context,
        )
        self.assertIn(
            "Software Developer",
            prompt_package.trusted_context,
        )
        self.assertIn(
            "Postgraduate software-development study.",
            prompt_package.untrusted_content,
        )

    def test_provider_is_called_with_resume_draft_output_model(self):
        provider = FakeResumeProvider()

        generate_resume_draft(
            student_profile=self.profile,
            ai_provider=provider,
        )

        self.assertIs(
            provider.calls[0]["output_model"],
            ResumeDraft,
        )

    def test_validated_resume_draft_is_returned(self):
        expected = ResumeDraft(
            professional_summary="Validated resume draft.",
            skills=["Python"],
            education=["Master of Information Technology"],
            experience=["IT Specialist at Example Company"],
            projects=["GradNavi"],
            missing_information=["Add measurable project outcomes."],
            limitations=["Generated from approved profile facts only."],
            is_draft=True,
            requires_user_review=True,
        )
        provider = FakeResumeProvider(
            response=expected,
        )

        result = generate_resume_draft(
            student_profile=self.profile,
            ai_provider=provider,
        )

        self.assertIs(
            result,
            expected,
        )

    def test_private_profile_fields_are_not_exposed_to_provider_prompt(self):
        provider = FakeResumeProvider()

        generate_resume_draft(
            student_profile=self.profile,
            ai_provider=provider,
        )

        prompt_package = provider.calls[0]["prompt_package"]
        serialized_prompt = (
            f"{prompt_package.trusted_context}\n"
            f"{prompt_package.untrusted_content}"
        )

        private_values = (
            self.user.email,
            self.user.first_name,
            self.user.last_name,
            "Private Interest",
            "private_personality_question",
            "private-personality-response",
            "https://private-project.example.com",
            "Internal skill metadata.",
            "Programming",
        )

        for value in private_values:
            with self.subTest(value=value):
                self.assertNotIn(
                    value,
                    serialized_prompt,
                )

    def test_shared_ai_provider_errors_propagate(self):
        provider = FakeResumeProvider(
            error=AIProviderTimeoutError("Provider timed out."),
        )

        with self.assertRaises(AIProviderTimeoutError):
            generate_resume_draft(
                student_profile=self.profile,
                ai_provider=provider,
            )

    def test_service_uses_injected_provider_only(self):
        provider = FakeResumeProvider()

        generate_resume_draft(
            student_profile=self.profile,
            ai_provider=provider,
        )

        self.assertEqual(
            len(provider.calls),
            1,
        )
