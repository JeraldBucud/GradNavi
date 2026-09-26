"""
Automated schema tests for GradNavi WBS 6.2.

These tests verify the shared Pydantic contracts used at the GradNavi
AI boundary.

The tests do not call an external AI provider.
"""

from datetime import date

from django.test import SimpleTestCase
from pydantic import ValidationError

from ai_services.schemas.common import (
    MAX_SKILLS,
    CareerGoalContext,
    EducationContext,
    ExperienceContext,
    ProjectContext,
    StudentProfileContext,
    StudentSkillContext,
)
from ai_services.schemas.inputs import (
    JOB_DESCRIPTION_MAX_LENGTH,
    LearningResourceDiscoveryInput,
    CoverLetterGenerationInput,
    InterviewFeedbackInput,
    InterviewQuestionInput,
    ResumeGenerationInput,
)
from ai_services.schemas.outputs import (
    CoverLetterDraft,
    DiscoveredLearningResourceCandidate,
    LearningResourceDiscoveryResult,
    InterviewFeedback,
    InterviewQuestion,
    InterviewQuestionSet,
    ResumeDraft,
)


class CommonSchemaTests(SimpleTestCase):
    """
    Tests for shared Student Profile AI-context schemas.
    """

    def test_valid_student_profile_context(self):
        profile = StudentProfileContext(
            skills=[
                StudentSkillContext(
                    name="Python",
                    proficiency_level="proficient",
                )
            ],
            education=[],
            experience=[],
            projects=[],
            career_goals=[],
        )

        self.assertEqual(
            profile.skills[0].name,
            "Python",
        )

    def test_student_profile_rejects_extra_field(self):
        with self.assertRaises(ValidationError):
            StudentProfileContext(
                skills=[],
                education=[],
                experience=[],
                projects=[],
                career_goals=[],
                email="student@example.com",
            )

    def test_skill_name_rejects_blank_value(self):
        with self.assertRaises(ValidationError):
            StudentSkillContext(
                name="   ",
                proficiency_level="proficient",
            )

    def test_skill_rejects_invalid_proficiency_level(self):
        with self.assertRaises(ValidationError):
            StudentSkillContext(
                name="Python",
                proficiency_level="expert",
            )

    def test_student_profile_enforces_skill_limit(self):
        skills = [
            StudentSkillContext(
                name=f"Skill {index}",
                proficiency_level="foundational",
            )
            for index in range(MAX_SKILLS + 1)
        ]

        with self.assertRaises(ValidationError):
            StudentProfileContext(
                skills=skills,
                education=[],
                experience=[],
                projects=[],
                career_goals=[],
            )

    def test_education_rejects_end_date_before_start_date(self):
        with self.assertRaises(ValidationError):
            EducationContext(
                institution_name="Example University",
                qualification="Master of Information Technology",
                field_of_study="Information Technology",
                start_date=date(2026, 1, 1),
                end_date=date(2025, 12, 31),
                description="",
            )

    def test_current_experience_rejects_end_date(self):
        with self.assertRaises(ValidationError):
            ExperienceContext(
                job_title="Software Developer",
                company="Example Company",
                start_date=date(2025, 1, 1),
                end_date=date(2026, 1, 1),
                is_current=True,
                description="",
            )

    def test_experience_rejects_end_date_before_start_date(self):
        with self.assertRaises(ValidationError):
            ExperienceContext(
                job_title="Software Developer",
                company="Example Company",
                start_date=date(2026, 1, 1),
                end_date=date(2025, 1, 1),
                is_current=False,
                description="",
            )

    def test_project_rejects_end_date_before_start_date(self):
        with self.assertRaises(ValidationError):
            ProjectContext(
                name="GradNavi",
                description="Career guidance project.",
                start_date=date(2026, 8, 1),
                end_date=date(2026, 7, 1),
            )

    def test_career_goal_rejects_blank_target_role(self):
        with self.assertRaises(ValidationError):
            CareerGoalContext(
                target_role="   ",
                description="",
            )


class InputSchemaTests(SimpleTestCase):
    """
    Tests for the four WBS 6.2 AI-operation input contracts.
    """

    def setUp(self):
        self.profile = StudentProfileContext(
            skills=[],
            education=[],
            experience=[],
            projects=[],
            career_goals=[],
        )

    def test_resume_generation_input_accepts_profile(self):
        request = ResumeGenerationInput(
            profile=self.profile,
            target_career_name="Software Developer",
        )

        self.assertEqual(
            request.profile,
            self.profile,
        )

        self.assertEqual(
            request.target_career_name,
            "Software Developer",
        )

    def test_cover_letter_rejects_blank_job_description(self):
        with self.assertRaises(ValidationError):
            CoverLetterGenerationInput(
                profile=self.profile,
                job_description="   ",
            )

    def test_cover_letter_enforces_job_description_limit(self):
        with self.assertRaises(ValidationError):
            CoverLetterGenerationInput(
                profile=self.profile,
                job_description="x" * (
                    JOB_DESCRIPTION_MAX_LENGTH + 1
                ),
            )

    def test_interview_question_default_count_is_five(self):
        request = InterviewQuestionInput(
            target_role="Software Developer",
        )

        self.assertEqual(
            request.question_count,
            5,
        )

    def test_interview_question_rejects_count_below_minimum(self):
        with self.assertRaises(ValidationError):
            InterviewQuestionInput(
                target_role="Software Developer",
                question_count=0,
            )

    def test_interview_question_rejects_count_above_maximum(self):
        with self.assertRaises(ValidationError):
            InterviewQuestionInput(
                target_role="Software Developer",
                question_count=11,
            )

    def test_interview_question_uses_strict_integer_validation(self):
        with self.assertRaises(ValidationError):
            InterviewQuestionInput(
                target_role="Software Developer",
                question_count="5",
            )

    def test_interview_question_rejects_blank_target_role(self):
        with self.assertRaises(ValidationError):
            InterviewQuestionInput(
                target_role="   ",
            )

    def test_interview_feedback_rejects_blank_answer(self):
        with self.assertRaises(ValidationError):
            InterviewFeedbackInput(
                target_role="Software Developer",
                question="Tell me about yourself.",
                student_answer="   ",
            )


class OutputSchemaTests(SimpleTestCase):
    """
    Tests for generated AI-output contracts.
    """

    def test_valid_resume_draft(self):
        draft = ResumeDraft(
            professional_summary="Software developer with Python experience.",
            skills=["Python"],
            education=[],
            experience=[],
            projects=[],
            missing_information=[],
            limitations=[],
            is_draft=True,
            requires_user_review=True,
        )

        self.assertTrue(draft.is_draft)
        self.assertTrue(draft.requires_user_review)

    def test_resume_draft_rejects_false_draft_flag(self):
        with self.assertRaises(ValidationError):
            ResumeDraft(
                professional_summary="Example summary.",
                skills=[],
                education=[],
                experience=[],
                projects=[],
                missing_information=[],
                limitations=[],
                is_draft=False,
                requires_user_review=True,
            )

    def test_resume_draft_rejects_extra_field(self):
        with self.assertRaises(ValidationError):
            ResumeDraft(
                professional_summary="Example summary.",
                skills=[],
                education=[],
                experience=[],
                projects=[],
                missing_information=[],
                limitations=[],
                is_draft=True,
                requires_user_review=True,
                email="student@example.com",
            )

    def test_resume_draft_rejects_wrong_skills_type(self):
        with self.assertRaises(ValidationError):
            ResumeDraft(
                professional_summary="Example summary.",
                skills="Python",
                education=[],
                experience=[],
                projects=[],
                missing_information=[],
                limitations=[],
                is_draft=True,
                requires_user_review=True,
            )

    def test_cover_letter_requires_body_paragraph(self):
        with self.assertRaises(ValidationError):
            CoverLetterDraft(
                opening="Dear Hiring Manager,",
                body_paragraphs=[],
                closing="Kind regards",
                matched_profile_facts=[],
                missing_information=[],
                limitations=[],
                is_draft=True,
                requires_user_review=True,
            )

    def test_interview_question_set_requires_question(self):
        with self.assertRaises(ValidationError):
            InterviewQuestionSet(
                questions=[],
                focus_areas=[],
                limitations=[],
                is_ai_generated=True,
                requires_user_review=True,
            )

    def test_valid_interview_question_set(self):
        result = InterviewQuestionSet(
            questions=[
                InterviewQuestion(
                    question="Tell me about a technical challenge.",
                    focus_area="Problem solving",
                )
            ],
            focus_areas=["Problem solving"],
            limitations=[],
            is_ai_generated=True,
            requires_user_review=True,
        )

        self.assertEqual(
            len(result.questions),
            1,
        )

    def test_interview_question_set_rejects_false_ai_flag(self):
        with self.assertRaises(ValidationError):
            InterviewQuestionSet(
                questions=[
                    InterviewQuestion(
                        question="Tell me about yourself.",
                        focus_area="Communication",
                    )
                ],
                focus_areas=["Communication"],
                limitations=[],
                is_ai_generated=False,
                requires_user_review=True,
            )

    def test_interview_feedback_rejects_hiring_probability(self):
        with self.assertRaises(ValidationError):
            InterviewFeedback(
                strengths=[],
                improvements=[],
                suggested_response="Example response.",
                feedback_summary="Example feedback.",
                limitations=[],
                is_ai_generated=True,
                requires_user_review=True,
                hiring_probability=95,
            )

    def test_valid_interview_feedback_requires_review(self):
        feedback = InterviewFeedback(
            strengths=["Clear explanation"],
            improvements=["Add a specific example"],
            suggested_response="A stronger example response.",
            feedback_summary="Good foundation with room for detail.",
            limitations=["AI-generated preparation feedback."],
            is_ai_generated=True,
            requires_user_review=True,
        )

        self.assertTrue(
            feedback.requires_user_review
        )


class LearningResourceDiscoverySchemaTests(
    SimpleTestCase
):
    def test_valid_discovery_input(
        self,
    ):
        request = (
            LearningResourceDiscoveryInput(
                skill_name=(
                    "Mathematics Knowledge"
                ),
                skill_description=(
                    "Knowledge of mathematics."
                ),
                career_name=(
                    "Software Engineer"
                ),
                access_type="free",
                requested_count=4,
                existing_urls=[
                    (
                        "https://example.com/"
                        "existing"
                    )
                ],
            )
        )

        self.assertEqual(
            request.requested_count,
            4,
        )

        self.assertEqual(
            request.access_type,
            "free",
        )


    def test_discovery_input_rejects_more_than_six(
        self,
    ):
        with self.assertRaises(
            ValidationError
        ):
            LearningResourceDiscoveryInput(
                skill_name="Python",
                requested_count=7,
            )


    def test_discovery_input_rejects_invalid_access_type(
        self,
    ):
        with self.assertRaises(
            ValidationError
        ):
            LearningResourceDiscoveryInput(
                skill_name="Python",
                access_type="subscription",
                requested_count=1,
            )


    def test_discovered_candidate_requires_http_url(
        self,
    ):
        with self.assertRaises(
            ValidationError
        ):
            DiscoveredLearningResourceCandidate(
                title="Example",
                provider="Example Provider",
                url="ftp://example.com/resource",
                resource_type="course",
                access_type="free",
                description="Example resource.",
            )


    def test_valid_discovery_result(
        self,
    ):
        result = (
            LearningResourceDiscoveryResult(
                candidates=[
                    DiscoveredLearningResourceCandidate(
                        title=(
                            "Example Mathematics Course"
                        ),
                        provider=(
                            "Example University"
                        ),
                        url=(
                            "https://example.edu/"
                            "mathematics"
                        ),
                        resource_type="course",
                        access_type="free",
                        description=(
                            "Mathematics learning resource."
                        ),
                    )
                ],
                is_ai_generated=True,
            )
        )

        self.assertEqual(
            len(
                result.candidates
            ),
            1,
        )


    def test_discovery_result_allows_zero_candidates(
        self,
    ):
        result = (
            LearningResourceDiscoveryResult(
                candidates=[],
                is_ai_generated=True,
            )
        )

        self.assertEqual(
            result.candidates,
            [],
        )


    def test_discovery_result_rejects_duplicate_urls(
        self,
    ):
        candidate = {
            "title": "Example Course",
            "provider": "Example Provider",
            "url": (
                "https://example.com/course"
            ),
            "resource_type": "course",
            "access_type": "free",
            "description": (
                "Example learning resource."
            ),
        }

        with self.assertRaises(
            ValidationError
        ):
            LearningResourceDiscoveryResult(
                candidates=[
                    candidate,
                    {
                        **candidate,
                        "title": (
                            "Duplicate Course"
                        ),
                    },
                ],
                is_ai_generated=True,
            )
