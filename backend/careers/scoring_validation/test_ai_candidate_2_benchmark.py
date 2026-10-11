"""
Local tests for GradNavi AI Candidate A2 benchmark helpers.

No external AI provider is contacted.
"""

from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from careers.scoring_validation.ai_candidate_2_benchmark import (
    build_unique_text_plan,
    rank_candidate_for_profile,
)

from careers.scoring_validation.ai_candidate_2_contexts import (
    A2CareerContext,
    AISemanticCandidate,
)


class A2BenchmarkHelperTests(
    SimpleTestCase
):
    def test_unique_text_plan_deduplicates_text(
        self,
    ):
        (
            texts,
            mapping,
        ) = build_unique_text_plan(
            (
                "Student",
                "Career A",
                "Career A",
                "Career B",
            )
        )

        self.assertEqual(
            texts,
            (
                "Student",
                "Career A",
                "Career B",
            ),
        )

        self.assertEqual(
            mapping["Student"],
            0,
        )

        self.assertEqual(
            mapping["Career A"],
            1,
        )

        self.assertEqual(
            mapping["Career B"],
            2,
        )

    def test_blank_embedding_text_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            build_unique_text_plan(
                (
                    "Student",
                    " ",
                )
            )

    def test_higher_similarity_ranks_first(
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
            1: A2CareerContext(
                career_id=1,
                career_name="Career A",
                candidate=(
                    AISemanticCandidate
                    .IDENTITY
                ),
                text="Career A text",
            ),
            2: A2CareerContext(
                career_id=2,
                career_name="Career B",
                candidate=(
                    AISemanticCandidate
                    .IDENTITY
                ),
                text="Career B text",
            ),
        }

        vectors = {
            "Career A text": (
                1.0,
                0.0,
            ),
            "Career B text": (
                0.0,
                1.0,
            ),
        }

        ranked = (
            rank_candidate_for_profile(
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
            )
        )

        self.assertEqual(
            ranked[0].career_name,
            "Career A",
        )

        self.assertEqual(
            ranked[0].rank,
            1,
        )

        self.assertEqual(
            ranked[0].similarity,
            Decimal("1.0"),
        )

    def test_equal_similarity_uses_name_tiebreak(
        self,
    ):
        career_z = SimpleNamespace(
            id=2,
            name="Zulu",
        )

        career_a = SimpleNamespace(
            id=1,
            name="Alpha",
        )

        contexts = {
            2: A2CareerContext(
                career_id=2,
                career_name="Zulu",
                candidate=(
                    AISemanticCandidate
                    .IDENTITY
                ),
                text="Zulu text",
            ),
            1: A2CareerContext(
                career_id=1,
                career_name="Alpha",
                candidate=(
                    AISemanticCandidate
                    .IDENTITY
                ),
                text="Alpha text",
            ),
        }

        vectors = {
            "Zulu text": (
                1.0,
                0.0,
            ),
            "Alpha text": (
                1.0,
                0.0,
            ),
        }

        ranked = (
            rank_candidate_for_profile(
                profile_vector=(
                    1.0,
                    0.0,
                ),
                careers=(
                    career_z,
                    career_a,
                ),
                contexts_by_career_id=(
                    contexts
                ),
                vectors_by_text=(
                    vectors
                ),
            )
        )

        self.assertEqual(
            ranked[0].career_name,
            "Alpha",
        )

        self.assertEqual(
            ranked[1].career_name,
            "Zulu",
        )
