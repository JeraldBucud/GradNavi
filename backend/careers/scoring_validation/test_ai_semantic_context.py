"""
Local tests for GradNavi AI Candidate A1 semantic context.

No external AI provider is contacted.
"""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from ai_services.exceptions import (
    AIInputError,
    AIMissingContextError,
)
from ai_services.schemas.common import (
    CareerGoalContext,
    EducationContext,
    ExperienceContext,
    ProjectContext,
    StudentProfileContext,
    StudentSkillContext,
)

from careers.scoring_validation.ai_semantic_context import (
    CareerEscoSemanticEvidence,
    CareerNumericalSemanticEvidence,
    CareerSemanticEvidence,
    CareerTechnologySemanticEvidence,
    build_career_semantic_context,
    build_student_semantic_context,
)


def make_student_context():
    """
    Build approved Sprint 4 profile context containing fields
    A1 both includes and deliberately excludes.
    """

    return StudentProfileContext(
        skills=[
            StudentSkillContext(
                name="Python",
                proficiency_level="proficient",
            ),
            StudentSkillContext(
                name="React",
                proficiency_level="developing",
            ),
        ],
        education=[
            EducationContext(
                institution_name=(
                    "Private University Name"
                ),
                qualification=(
                    "Master of Information Technology"
                ),
                field_of_study=(
                    "Software Development"
                ),
                start_date=date(
                    2025,
                    1,
                    1,
                ),
                end_date=None,
                description=(
                    "Backend and software engineering study."
                ),
            ),
        ],
        experience=[
            ExperienceContext(
                job_title=(
                    "Software Developer"
                ),
                company=(
                    "Private Company Name"
                ),
                start_date=date(
                    2024,
                    1,
                    1,
                ),
                end_date=None,
                is_current=True,
                description=(
                    "Developed web applications using Python."
                ),
            ),
        ],
        projects=[
            ProjectContext(
                name="GradNavi",
                description=(
                    "AI-powered career guidance project."
                ),
                start_date=date(
                    2026,
                    1,
                    1,
                ),
                end_date=None,
            ),
        ],
        career_goals=[
            CareerGoalContext(
                target_role=(
                    "Software Engineer"
                ),
                description=(
                    "Build backend and full-stack systems."
                ),
            ),
        ],
    )


class StudentSemanticContextTests(
    SimpleTestCase
):
    """
    Validate A1 Student privacy minimisation.
    """

    @patch(
        "careers.scoring_validation."
        "ai_semantic_context."
        "build_student_profile_context"
    )
    def test_approved_career_information_is_included(
        self,
        mocked_builder,
    ):
        mocked_builder.return_value = (
            make_student_context()
        )

        result = (
            build_student_semantic_context(
                student_profile=object()
            )
        )

        self.assertIn(
            "Python",
            result.text,
        )

        self.assertIn(
            "proficient",
            result.text,
        )

        self.assertIn(
            "Master of Information Technology",
            result.text,
        )

        self.assertIn(
            "Software Development",
            result.text,
        )

        self.assertIn(
            "Software Developer",
            result.text,
        )

        self.assertIn(
            "GradNavi",
            result.text,
        )

        self.assertIn(
            "Software Engineer",
            result.text,
        )

    @patch(
        "careers.scoring_validation."
        "ai_semantic_context."
        "build_student_profile_context"
    )
    def test_semantic_text_excludes_institution_company_and_dates(
        self,
        mocked_builder,
    ):
        mocked_builder.return_value = (
            make_student_context()
        )

        result = (
            build_student_semantic_context(
                student_profile=object()
            )
        )

        self.assertNotIn(
            "Private University Name",
            result.text,
        )

        self.assertNotIn(
            "Private Company Name",
            result.text,
        )

        self.assertNotIn(
            "2025",
            result.text,
        )

        self.assertNotIn(
            "2024",
            result.text,
        )

        self.assertNotIn(
            "2026",
            result.text,
        )

    @patch(
        "careers.scoring_validation."
        "ai_semantic_context."
        "build_student_profile_context"
    )
    def test_counts_are_recorded(
        self,
        mocked_builder,
    ):
        mocked_builder.return_value = (
            make_student_context()
        )

        result = (
            build_student_semantic_context(
                student_profile=object()
            )
        )

        self.assertEqual(
            result.skill_count,
            2,
        )

        self.assertEqual(
            result.education_count,
            1,
        )

        self.assertEqual(
            result.experience_count,
            1,
        )

        self.assertEqual(
            result.project_count,
            1,
        )

        self.assertEqual(
            result.career_goal_count,
            1,
        )

    @patch(
        "careers.scoring_validation."
        "ai_semantic_context."
        "build_student_profile_context"
    )
    def test_empty_profile_is_rejected(
        self,
        mocked_builder,
    ):
        mocked_builder.return_value = (
            StudentProfileContext(
                skills=[],
                education=[],
                experience=[],
                projects=[],
                career_goals=[],
            )
        )

        with self.assertRaises(
            AIMissingContextError
        ):
            build_student_semantic_context(
                student_profile=object()
            )


class CareerSemanticContextTests(
    SimpleTestCase
):
    """
    Validate deterministic A1 Career context.
    """

    def make_career(
        self,
        *,
        active=True,
    ):
        return SimpleNamespace(
            active=active,
            name="Software Engineer",
            category="Information Technology",
            description=(
                "Designs and develops software systems."
            ),
        )

    def make_evidence(
        self,
    ):
        return CareerSemanticEvidence(
            numerical=(
                CareerNumericalSemanticEvidence(
                    skill_name=(
                        "Programming"
                    ),
                    concept_type="skill",
                    normalized_importance=(
                        Decimal("85.00")
                    ),
                    normalized_level=(
                        Decimal("75.00")
                    ),
                ),
            ),
            technologies=(
                CareerTechnologySemanticEvidence(
                    skill_name="Python",
                    concept_type="technology",
                    in_demand_percentage=(
                        Decimal("29.00")
                    ),
                ),
            ),
            esco=(
                CareerEscoSemanticEvidence(
                    skill_name=(
                        "develop software"
                    ),
                    concept_type="skill",
                    relation="essential",
                ),
            ),
        )

    @patch(
        "careers.scoring_validation."
        "ai_semantic_context."
        "load_career_semantic_evidence"
    )
    def test_career_context_contains_all_approved_sections(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            self.make_evidence()
        )

        result = (
            build_career_semantic_context(
                career=self.make_career()
            )
        )

        self.assertIn(
            "Software Engineer",
            result.text,
        )

        self.assertIn(
            "Information Technology",
            result.text,
        )

        self.assertIn(
            "Programming",
            result.text,
        )

        self.assertIn(
            "importance: 85",
            result.text,
        )

        self.assertIn(
            "Python",
            result.text,
        )

        self.assertIn(
            "demand: 29%",
            result.text,
        )

        self.assertIn(
            "develop software",
            result.text,
        )

        self.assertIn(
            "relation: essential",
            result.text,
        )

    @patch(
        "careers.scoring_validation."
        "ai_semantic_context."
        "load_career_semantic_evidence"
    )
    def test_career_evidence_counts_are_recorded(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            self.make_evidence()
        )

        result = (
            build_career_semantic_context(
                career=self.make_career()
            )
        )

        self.assertEqual(
            result.numerical_competency_count,
            1,
        )

        self.assertEqual(
            result.technology_count,
            1,
        )

        self.assertEqual(
            result.esco_relationship_count,
            1,
        )

    def test_inactive_career_is_rejected(
        self,
    ):
        with self.assertRaises(
            AIInputError
        ):
            build_career_semantic_context(
                career=self.make_career(
                    active=False
                )
            )
