"""
Local tests for GradNavi AI Candidate A3.

No OpenAI request is made.
"""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from careers.scoring_validation.ai_candidate_3 import (
    A3WeightingCandidate,
    build_a3_career_contexts,
    build_a3_result,
    combine_a3_semantic_similarity,
    rank_a3_results,
)

from careers.scoring_validation.ai_semantic_context import (
    CareerEscoSemanticEvidence,
    CareerSemanticEvidence,
)


def make_career():
    return SimpleNamespace(
        id=10,
        active=True,
        name="Software Engineer",
        category=(
            "Software and Information Technology"
        ),
        description=(
            "Designs and develops software systems."
        ),
    )


def make_esco_evidence():
    return CareerSemanticEvidence(
        numerical=(),
        technologies=(),
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
        ),
    )


class A3SemanticScoringTests(
    SimpleTestCase
):
    def test_a3_90_weighting(
        self,
    ):
        result = (
            combine_a3_semantic_similarity(
                identity_similarity=(
                    Decimal("0.80")
                ),
                esco_similarity=(
                    Decimal("0.60")
                ),
                candidate=(
                    A3WeightingCandidate
                    .IDENTITY_90_ESCO_10
                ),
            )
        )

        self.assertEqual(
            result,
            Decimal("0.780000"),
        )

    def test_a3_80_weighting(
        self,
    ):
        result = (
            combine_a3_semantic_similarity(
                identity_similarity=(
                    Decimal("0.80")
                ),
                esco_similarity=(
                    Decimal("0.60")
                ),
                candidate=(
                    A3WeightingCandidate
                    .IDENTITY_80_ESCO_20
                ),
            )
        )

        self.assertEqual(
            result,
            Decimal("0.760000"),
        )

    def test_a3_70_weighting(
        self,
    ):
        result = (
            combine_a3_semantic_similarity(
                identity_similarity=(
                    Decimal("0.80")
                ),
                esco_similarity=(
                    Decimal("0.60")
                ),
                candidate=(
                    A3WeightingCandidate
                    .IDENTITY_70_ESCO_30
                ),
            )
        )

        self.assertEqual(
            result,
            Decimal("0.740000"),
        )

    def test_a3_60_weighting(
        self,
    ):
        result = (
            combine_a3_semantic_similarity(
                identity_similarity=(
                    Decimal("0.80")
                ),
                esco_similarity=(
                    Decimal("0.60")
                ),
                candidate=(
                    A3WeightingCandidate
                    .IDENTITY_60_ESCO_40
                ),
            )
        )

        self.assertEqual(
            result,
            Decimal("0.720000"),
        )

    def test_missing_esco_uses_identity_only(
        self,
    ):
        result = (
            combine_a3_semantic_similarity(
                identity_similarity=(
                    Decimal("0.63")
                ),
                esco_similarity=None,
                candidate=(
                    A3WeightingCandidate
                    .IDENTITY_60_ESCO_40
                ),
            )
        )

        self.assertEqual(
            result,
            Decimal("0.630000"),
        )

    def test_negative_similarity_maps_to_zero(
        self,
    ):
        result = (
            combine_a3_semantic_similarity(
                identity_similarity=(
                    Decimal("0.50")
                ),
                esco_similarity=(
                    Decimal("-0.40")
                ),
                candidate=(
                    A3WeightingCandidate
                    .IDENTITY_80_ESCO_20
                ),
            )
        )

        self.assertEqual(
            result,
            Decimal("0.400000"),
        )

    def test_score_uses_zero_to_100_scale(
        self,
    ):
        result = build_a3_result(
            career_id=1,
            career_name="Career",
            candidate=(
                A3WeightingCandidate
                .IDENTITY_80_ESCO_20
            ),
            identity_similarity=(
                Decimal("0.80")
            ),
            esco_similarity=(
                Decimal("0.60")
            ),
        )

        self.assertEqual(
            result.semantic_alignment_ratio,
            Decimal("0.760000"),
        )

        self.assertEqual(
            result.semantic_alignment_score,
            Decimal("76.00"),
        )

    def test_higher_combined_score_ranks_first(
        self,
    ):
        first = build_a3_result(
            career_id=1,
            career_name="Career A",
            candidate=(
                A3WeightingCandidate
                .IDENTITY_80_ESCO_20
            ),
            identity_similarity=(
                Decimal("0.80")
            ),
            esco_similarity=(
                Decimal("0.80")
            ),
        )

        second = build_a3_result(
            career_id=2,
            career_name="Career B",
            candidate=(
                A3WeightingCandidate
                .IDENTITY_80_ESCO_20
            ),
            identity_similarity=(
                Decimal("0.60")
            ),
            esco_similarity=(
                Decimal("0.60")
            ),
        )

        ranked = rank_a3_results(
            (
                second,
                first,
            )
        )

        self.assertEqual(
            ranked[0].career_id,
            1,
        )

        self.assertEqual(
            ranked[0].rank,
            1,
        )

        self.assertEqual(
            ranked[1].rank,
            2,
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_3."
        "load_career_semantic_evidence"
    )
    def test_a3_context_contains_separate_esco_text(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            make_esco_evidence()
        )

        context = (
            build_a3_career_contexts(
                career=make_career()
            )
        )

        self.assertIn(
            "Software Engineer",
            context.identity_text,
        )

        self.assertIn(
            "develop source code",
            context.essential_esco_text,
        )

        self.assertNotIn(
            "develop source code",
            context.identity_text,
        )

        self.assertEqual(
            context.essential_esco_count,
            2,
        )

    @patch(
        "careers.scoring_validation."
        "ai_candidate_3."
        "load_career_semantic_evidence"
    )
    def test_missing_esco_context_is_none(
        self,
        mocked_loader,
    ):
        mocked_loader.return_value = (
            CareerSemanticEvidence(
                numerical=(),
                technologies=(),
                esco=(),
            )
        )

        context = (
            build_a3_career_contexts(
                career=make_career()
            )
        )

        self.assertIsNone(
            context.essential_esco_text
        )

        self.assertEqual(
            context.essential_esco_count,
            0,
        )
