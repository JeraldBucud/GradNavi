"""
Tests for GradNavi AI Candidate A2 Career contexts.

No external AI provider is contacted.
"""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from careers.scoring_validation.ai_candidate_2_contexts import (
    AISemanticCandidate,
    MAX_ESSENTIAL_ESCO_SKILLS,
    MAX_IN_DEMAND_TECHNOLOGIES,
    build_a2_identity_context,
    build_a2_identity_esco_context,
    build_a2_identity_technology_context,
    build_all_a2_contexts,
)

from careers.scoring_validation.ai_semantic_context import (
    CareerEscoSemanticEvidence,
    CareerSemanticEvidence,
    CareerTechnologySemanticEvidence,
)


def make_career(
    *,
    active=True,
):
    return SimpleNamespace(
        id=3,
        active=active,
        name="Software Engineer",
        category=(
            "Software and Information Technology"
        ),
        description=(
            "Designs, develops, tests, maintains, "
            "and improves software systems."
        ),
    )


def make_evidence():
    return CareerSemanticEvidence(
        numerical=(),
        technologies=(
            CareerTechnologySemanticEvidence(
                skill_name="Python",
                concept_type="technology",
                in_demand_percentage=(
                    Decimal("29")
                ),
            ),
            CareerTechnologySemanticEvidence(
                skill_name="Java",
                concept_type="technology",
                in_demand_percentage=(
                    Decimal("25")
                ),
            ),
        ),
        esco=(
            CareerEscoSemanticEvidence(
                skill_name="develop software",
                concept_type="skill",
                relation="essential",
            ),
            CareerEscoSemanticEvidence(
                skill_name="debug software",
                concept_type="skill",
                relation="essential",
            ),
            CareerEscoSemanticEvidence(
                skill_name="write documentation",
                concept_type="skill",
                relation="optional",
            ),
        ),
    )


class A2CareerContextTests(
    SimpleTestCase
):
    def test_identity_contains_only_career_metadata(
        self,
    ):
        result = (
            build_a2_identity_context(
                career=make_career()
            )
        )

        self.assertEqual(
            result.candidate,
            AISemanticCandidate.IDENTITY,
        )

        self.assertIn(
            "Software Engineer",
            result.text,
        )

        self.assertIn(
            "Software and Information Technology",
            result.text,
        )

        self.assertNotIn(
            "Python",
            result.text,
        )

        self.assertNotIn(
            "develop software",
            result.text,
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_2_contexts."
        "load_career_semantic_evidence"
    )
    def test_identity_esco_keeps_only_essential_skills(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_evidence()
        )

        result = (
            build_a2_identity_esco_context(
                career=make_career()
            )
        )

        self.assertIn(
            "develop software",
            result.text,
        )

        self.assertIn(
            "debug software",
            result.text,
        )

        self.assertNotIn(
            "write documentation",
            result.text,
        )

        self.assertNotIn(
            "Python",
            result.text,
        )

        self.assertEqual(
            result.essential_esco_count,
            2,
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_2_contexts."
        "load_career_semantic_evidence"
    )
    def test_identity_technology_keeps_demand_signal(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_evidence()
        )

        result = (
            build_a2_identity_technology_context(
                career=make_career()
            )
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
            "Java",
            result.text,
        )

        self.assertNotIn(
            "develop software",
            result.text,
        )

        self.assertEqual(
            result.technology_count,
            2,
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_2_contexts."
        "load_career_semantic_evidence"
    )
    def test_all_three_variants_are_built(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_evidence()
        )

        results = (
            build_all_a2_contexts(
                career=make_career()
            )
        )

        self.assertEqual(
            len(
                results
            ),
            3,
        )

        self.assertEqual(
            {
                result.candidate
                for result
                in results
            },
            {
                AISemanticCandidate.IDENTITY,
                AISemanticCandidate.IDENTITY_ESCO,
                AISemanticCandidate.IDENTITY_TECHNOLOGY,
            },
        )

    def test_inactive_career_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            build_a2_identity_context(
                career=make_career(
                    active=False
                )
            )

    def test_limits_are_small_and_explicit(
        self,
    ):
        self.assertEqual(
            MAX_ESSENTIAL_ESCO_SKILLS,
            12,
        )

        self.assertEqual(
            MAX_IN_DEMAND_TECHNOLOGIES,
            10,
        )
