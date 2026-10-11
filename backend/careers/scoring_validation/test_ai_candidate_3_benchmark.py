"""
Local tests for the GradNavi A3 benchmark runner.

No external AI provider is contacted.
"""

from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from careers.scoring_validation.ai_candidate_3 import (
    A3CareerContexts,
    A3WeightingCandidate,
)

from careers.scoring_validation.ai_candidate_3_benchmark import (
    rank_a3_profile,
)


class A3BenchmarkHelperTests(
    SimpleTestCase
):
    def test_identity_and_esco_similarity_are_combined(
        self,
    ):
        career_a = SimpleNamespace(
            id=1,
            name="Career A",
        )

        career_b = SimpleNamespace(
            id=2,
            name="Career B",
        )

        contexts = {
            1: A3CareerContexts(
                career_id=1,
                career_name="Career A",
                identity_text="A identity",
                essential_esco_text="A esco",
                essential_esco_count=1,
            ),
            2: A3CareerContexts(
                career_id=2,
                career_name="Career B",
                identity_text="B identity",
                essential_esco_text="B esco",
                essential_esco_count=1,
            ),
        }

        vectors = {
            "A identity": (
                1.0,
                0.0,
            ),
            "A esco": (
                1.0,
                0.0,
            ),
            "B identity": (
                0.8,
                0.6,
            ),
            "B esco": (
                0.0,
                1.0,
            ),
        }

        ranked = rank_a3_profile(
            profile_vector=(
                1.0,
                0.0,
            ),
            careers=(
                career_a,
                career_b,
            ),
            contexts_by_career_id=(
                contexts
            ),
            vectors_by_text=(
                vectors
            ),
            candidate=(
                A3WeightingCandidate
                .IDENTITY_80_ESCO_20
            ),
        )

        self.assertEqual(
            ranked[0].career_id,
            1,
        )

        self.assertEqual(
            ranked[0].rank,
            1,
        )

    def test_missing_esco_uses_identity_similarity(
        self,
    ):
        career = SimpleNamespace(
            id=1,
            name="Cyber Career",
        )

        contexts = {
            1: A3CareerContexts(
                career_id=1,
                career_name="Cyber Career",
                identity_text="Cyber identity",
                essential_esco_text=None,
                essential_esco_count=0,
            ),
        }

        vectors = {
            "Cyber identity": (
                1.0,
                0.0,
            ),
        }

        ranked = rank_a3_profile(
            profile_vector=(
                1.0,
                0.0,
            ),
            careers=(
                career,
            ),
            contexts_by_career_id=(
                contexts
            ),
            vectors_by_text=(
                vectors
            ),
            candidate=(
                A3WeightingCandidate
                .IDENTITY_60_ESCO_40
            ),
        )

        self.assertEqual(
            ranked[0]
            .semantic_alignment_ratio,
            Decimal("1.000000"),
        )

        self.assertIsNone(
            ranked[0]
            .esco_similarity
        )

    def test_weighting_changes_combined_result(
        self,
    ):
        career_a = SimpleNamespace(
            id=1,
            name="Identity Strong",
        )

        career_b = SimpleNamespace(
            id=2,
            name="ESCO Strong",
        )

        contexts = {
            1: A3CareerContexts(
                career_id=1,
                career_name="Identity Strong",
                identity_text="identity strong",
                essential_esco_text="esco weak",
                essential_esco_count=1,
            ),
            2: A3CareerContexts(
                career_id=2,
                career_name="ESCO Strong",
                identity_text="identity weaker",
                essential_esco_text="esco strong",
                essential_esco_count=1,
            ),
        }

        vectors = {
            "identity strong": (
                1.0,
                0.0,
            ),
            "esco weak": (
                0.0,
                1.0,
            ),
            "identity weaker": (
                0.8,
                0.6,
            ),
            "esco strong": (
                1.0,
                0.0,
            ),
        }

        ranked_90 = rank_a3_profile(
            profile_vector=(
                1.0,
                0.0,
            ),
            careers=(
                career_a,
                career_b,
            ),
            contexts_by_career_id=(
                contexts
            ),
            vectors_by_text=(
                vectors
            ),
            candidate=(
                A3WeightingCandidate
                .IDENTITY_90_ESCO_10
            ),
        )

        ranked_60 = rank_a3_profile(
            profile_vector=(
                1.0,
                0.0,
            ),
            careers=(
                career_a,
                career_b,
            ),
            contexts_by_career_id=(
                contexts
            ),
            vectors_by_text=(
                vectors
            ),
            candidate=(
                A3WeightingCandidate
                .IDENTITY_60_ESCO_40
            ),
        )

        self.assertEqual(
            ranked_90[0].career_id,
            1,
        )

        self.assertEqual(
            ranked_60[0].career_id,
            2,
        )
