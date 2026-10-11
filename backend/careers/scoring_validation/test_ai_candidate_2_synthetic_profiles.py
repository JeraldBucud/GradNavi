"""
Tests for GradNavi AI Candidate A2 synthetic profiles.

No external AI provider is contacted.
"""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from careers.scoring_validation.ai_candidate_2_synthetic_profiles import (
    AISemanticBenchmarkScenario,
    MAX_BENCHMARK_NUMERICAL_COMPETENCIES,
    build_a2_synthetic_profile,
    take_deterministic_half,
)

from careers.scoring_validation.ai_semantic_context import (
    CareerEscoSemanticEvidence,
    CareerNumericalSemanticEvidence,
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
            "Designs and develops software systems."
        ),
    )


def make_evidence():
    return CareerSemanticEvidence(
        numerical=(
            CareerNumericalSemanticEvidence(
                skill_name=(
                    "Computers and Electronics"
                ),
                concept_type="knowledge",
                normalized_importance=(
                    Decimal("93.75")
                ),
                normalized_level=(
                    Decimal("89")
                ),
            ),
            CareerNumericalSemanticEvidence(
                skill_name=(
                    "Critical Thinking"
                ),
                concept_type="skill",
                normalized_importance=(
                    Decimal("72")
                ),
                normalized_level=(
                    Decimal("58")
                ),
            ),
            CareerNumericalSemanticEvidence(
                skill_name=(
                    "Systems Analysis"
                ),
                concept_type="skill",
                normalized_importance=(
                    Decimal("62")
                ),
                normalized_level=(
                    Decimal("55")
                ),
            ),
        ),
        technologies=(
            CareerTechnologySemanticEvidence(
                skill_name="Python",
                concept_type="technology",
                in_demand_percentage=(
                    Decimal("29")
                ),
            ),
            CareerTechnologySemanticEvidence(
                skill_name="JavaScript",
                concept_type="technology",
                in_demand_percentage=(
                    Decimal("20")
                ),
            ),
            CareerTechnologySemanticEvidence(
                skill_name="Docker",
                concept_type="technology",
                in_demand_percentage=(
                    Decimal("13")
                ),
            ),
        ),
        esco=(
            CareerEscoSemanticEvidence(
                skill_name="develop source code",
                concept_type="skill",
                relation="essential",
            ),
            CareerEscoSemanticEvidence(
                skill_name="debug source code",
                concept_type="skill",
                relation="essential",
            ),
            CareerEscoSemanticEvidence(
                skill_name="test software",
                concept_type="skill",
                relation="essential",
            ),
        ),
    )


class A2SyntheticProfileTests(
    SimpleTestCase
):
    def test_deterministic_half_keeps_larger_half(
        self,
    ):
        result = (
            take_deterministic_half(
                (
                    "a",
                    "b",
                    "c",
                )
            )
        )

        self.assertEqual(
            result,
            (
                "a",
                "b",
            ),
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_2_synthetic_profiles."
        "load_career_semantic_evidence"
    )
    def test_full_signal_contains_all_selected_evidence(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_evidence()
        )

        result = (
            build_a2_synthetic_profile(
                career=make_career(),
                scenario=(
                    AISemanticBenchmarkScenario
                    .FULL_SIGNAL
                ),
            )
        )

        self.assertIn(
            "Computers and Electronics",
            result.text,
        )

        self.assertIn(
            "develop source code",
            result.text,
        )

        self.assertIn(
            "Python",
            result.text,
        )

        self.assertEqual(
            result.numerical_competency_count,
            3,
        )

        self.assertEqual(
            result.essential_esco_count,
            3,
        )

        self.assertEqual(
            result.technology_count,
            3,
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_2_synthetic_profiles."
        "load_career_semantic_evidence"
    )
    def test_half_signal_reduces_each_signal(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_evidence()
        )

        result = (
            build_a2_synthetic_profile(
                career=make_career(),
                scenario=(
                    AISemanticBenchmarkScenario
                    .HALF_SIGNAL
                ),
            )
        )

        self.assertEqual(
            result.numerical_competency_count,
            2,
        )

        self.assertEqual(
            result.essential_esco_count,
            2,
        )

        self.assertEqual(
            result.technology_count,
            2,
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_2_synthetic_profiles."
        "load_career_semantic_evidence"
    )
    def test_target_career_metadata_is_not_in_profile(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_evidence()
        )

        result = (
            build_a2_synthetic_profile(
                career=make_career(),
                scenario=(
                    AISemanticBenchmarkScenario
                    .FULL_SIGNAL
                ),
            )
        )

        self.assertNotIn(
            "Software Engineer",
            result.text,
        )

        self.assertNotIn(
            "Software and Information Technology",
            result.text,
        )

        self.assertNotIn(
            "Designs and develops software systems.",
            result.text,
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_2_synthetic_profiles."
        "load_career_semantic_evidence"
    )
    def test_legitimate_career_term_overlap_is_allowed(
        self,
        mocked_loader,
    ):
        base_evidence = (
            make_evidence()
        )

        mocked_loader.return_value = (
            CareerSemanticEvidence(
                numerical=(
                    base_evidence.numerical
                ),
                technologies=(
                    base_evidence.technologies
                ),
                esco=(
                    base_evidence.esco
                    + (
                        CareerEscoSemanticEvidence(
                            skill_name=(
                                "cyber security"
                            ),
                            concept_type="skill",
                            relation="essential",
                        ),
                    )
                ),
            )
        )

        career = SimpleNamespace(
            id=4,
            active=True,
            name=(
                "Cyber Security Advice "
                "and Assessment Specialist"
            ),
            category="Cyber Security",
            description=(
                "Provides security advice "
                "and assessment services."
            ),
        )

        result = (
            build_a2_synthetic_profile(
                career=career,
                scenario=(
                    AISemanticBenchmarkScenario
                    .FULL_SIGNAL
                ),
            )
        )

        self.assertIn(
            "- cyber security",
            result.text.casefold(),
        )


    def test_inactive_career_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            build_a2_synthetic_profile(
                career=make_career(
                    active=False
                ),
                scenario=(
                    AISemanticBenchmarkScenario
                    .FULL_SIGNAL
                ),
            )

    def test_numerical_limit_is_explicit(
        self,
    ):
        self.assertEqual(
            MAX_BENCHMARK_NUMERICAL_COMPETENCIES,
            12,
        )
