"""
Unit tests for GradNavi AI Candidate A1.

No OpenAI request is made.

Fake embedding vectors validate A1 scoring,
ranking, error handling, and usage reporting.
"""

from decimal import Decimal
from pathlib import Path

from django.test import SimpleTestCase

from ai_services.exceptions import (
    AIInputError,
    AIResponseValidationError,
)
from ai_services.providers.embeddings import (
    EmbeddingBatchResult,
)

from careers.scoring_validation.ai_candidate_1 import (
    SemanticCareerInput,
    calculate_cosine_similarity,
    calculate_semantic_alignment,
    score_ai_candidate_1,
)
from careers.services.recommendation_scoring import (
    ScoreStatus,
)


class FakeEmbeddingProvider:
    """
    Deterministic fake provider for A1 tests.
    """

    def __init__(
        self,
        *,
        vectors,
        model="fake-embedding-model",
        prompt_tokens=20,
        total_tokens=20,
    ):
        self.vectors = tuple(
            tuple(
                vector
            )
            for vector
            in vectors
        )

        self.model = model

        self.prompt_tokens = (
            prompt_tokens
        )

        self.total_tokens = (
            total_tokens
        )

        self.calls = []

    def embed_texts(
        self,
        *,
        texts,
    ):
        self.calls.append(
            tuple(
                texts
            )
        )

        return EmbeddingBatchResult(
            vectors=self.vectors,
            model=self.model,
            prompt_tokens=(
                self.prompt_tokens
            ),
            total_tokens=(
                self.total_tokens
            ),
        )


def career(
    career_id,
    name,
    text,
):
    return SemanticCareerInput(
        career_id=career_id,
        career_name=name,
        semantic_text=text,
    )


class AICandidate1ScoringTests(
    SimpleTestCase
):
    def test_identical_vector_scores_100(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
                (
                    1.0,
                    0.0,
                ),
            )
        )

        report = score_ai_candidate_1(
            student_semantic_text=(
                "Python software development"
            ),
            careers=(
                career(
                    1,
                    "Software Engineer",
                    "Software engineering",
                ),
            ),
            embedding_provider=provider,
        )

        result = report.results[0]

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.semantic_alignment_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.rank,
            1,
        )

    def test_orthogonal_vector_scores_zero(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
                (
                    0.0,
                    1.0,
                ),
            )
        )

        report = score_ai_candidate_1(
            student_semantic_text="Student",
            careers=(
                career(
                    1,
                    "Career",
                    "Career context",
                ),
            ),
            embedding_provider=provider,
        )

        self.assertEqual(
            report.results[0]
            .semantic_alignment_score,
            Decimal("0.00"),
        )

    def test_negative_similarity_maps_to_zero(
        self,
    ):
        (
            ratio,
            score,
        ) = calculate_semantic_alignment(
            cosine_similarity=(
                Decimal("-0.75")
            )
        )

        self.assertEqual(
            ratio,
            Decimal("0"),
        )

        self.assertEqual(
            score,
            Decimal("0.00"),
        )

    def test_higher_semantic_alignment_ranks_first(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
                (
                    1.0,
                    0.0,
                ),
                (
                    0.6,
                    0.8,
                ),
                (
                    0.0,
                    1.0,
                ),
            )
        )

        report = score_ai_candidate_1(
            student_semantic_text="Student",
            careers=(
                career(
                    1,
                    "Software Engineer",
                    "Software",
                ),
                career(
                    2,
                    "Data Analyst",
                    "Data",
                ),
                career(
                    3,
                    "Nurse",
                    "Nursing",
                ),
            ),
            embedding_provider=provider,
        )

        self.assertEqual(
            [
                result.career_name
                for result
                in report.results
            ],
            [
                "Software Engineer",
                "Data Analyst",
                "Nurse",
            ],
        )

        self.assertEqual(
            [
                result.rank
                for result
                in report.results
            ],
            [
                1,
                2,
                3,
            ],
        )

    def test_identical_alignment_uses_name_tiebreak(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
                (
                    1.0,
                    0.0,
                ),
                (
                    1.0,
                    0.0,
                ),
            )
        )

        report = score_ai_candidate_1(
            student_semantic_text="Student",
            careers=(
                career(
                    2,
                    "Zulu Career",
                    "Zulu",
                ),
                career(
                    1,
                    "Alpha Career",
                    "Alpha",
                ),
            ),
            embedding_provider=provider,
        )

        self.assertEqual(
            report.results[0].career_name,
            "Alpha Career",
        )

        self.assertEqual(
            report.results[1].career_name,
            "Zulu Career",
        )

    def test_empty_student_is_insufficient_profile(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=()
        )

        report = score_ai_candidate_1(
            student_semantic_text=" ",
            careers=(
                career(
                    1,
                    "Software Engineer",
                    "Software",
                ),
            ),
            embedding_provider=provider,
        )

        result = report.results[0]

        self.assertEqual(
            result.score_status,
            ScoreStatus.INSUFFICIENT_PROFILE,
        )

        self.assertIsNone(
            result.rank
        )

        self.assertEqual(
            provider.calls,
            [],
        )

    def test_blank_career_is_insufficient_evidence(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
                (
                    1.0,
                    0.0,
                ),
            )
        )

        report = score_ai_candidate_1(
            student_semantic_text="Student",
            careers=(
                career(
                    1,
                    "Blank Career",
                    " ",
                ),
                career(
                    2,
                    "Software Engineer",
                    "Software",
                ),
            ),
            embedding_provider=provider,
        )

        scored = next(
            result
            for result
            in report.results
            if result.career_id == 2
        )

        unscored = next(
            result
            for result
            in report.results
            if result.career_id == 1
        )

        self.assertEqual(
            scored.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            unscored.score_status,
            ScoreStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            unscored.rank
        )

    def test_batch_provider_is_called_once(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
                (
                    1.0,
                    0.0,
                ),
                (
                    0.0,
                    1.0,
                ),
            )
        )

        score_ai_candidate_1(
            student_semantic_text=(
                "  Student context  "
            ),
            careers=(
                career(
                    1,
                    "Career A",
                    " Career A context ",
                ),
                career(
                    2,
                    "Career B",
                    "Career B context",
                ),
            ),
            embedding_provider=provider,
        )

        self.assertEqual(
            len(
                provider.calls
            ),
            1,
        )

        self.assertEqual(
            provider.calls[0],
            (
                "Student context",
                "Career A context",
                "Career B context",
            ),
        )

    def test_usage_metadata_is_preserved(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
                (
                    1.0,
                    0.0,
                ),
            ),
            model="test-model",
            prompt_tokens=37,
            total_tokens=37,
        )

        report = score_ai_candidate_1(
            student_semantic_text="Student",
            careers=(
                career(
                    1,
                    "Career",
                    "Career",
                ),
            ),
            embedding_provider=provider,
        )

        self.assertEqual(
            report.model,
            "test-model",
        )

        self.assertEqual(
            report.prompt_tokens,
            37,
        )

        self.assertEqual(
            report.total_tokens,
            37,
        )

    def test_duplicate_career_is_rejected(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=()
        )

        with self.assertRaises(
            AIInputError
        ):
            score_ai_candidate_1(
                student_semantic_text="Student",
                careers=(
                    career(
                        1,
                        "Career A",
                        "A",
                    ),
                    career(
                        1,
                        "Career B",
                        "B",
                    ),
                ),
                embedding_provider=provider,
            )

    def test_mismatched_vector_count_is_rejected(
        self,
    ):
        provider = FakeEmbeddingProvider(
            vectors=(
                (
                    1.0,
                    0.0,
                ),
            )
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            score_ai_candidate_1(
                student_semantic_text="Student",
                careers=(
                    career(
                        1,
                        "Career",
                        "Career",
                    ),
                ),
                embedding_provider=provider,
            )

    def test_zero_vector_is_rejected(
        self,
    ):
        with self.assertRaises(
            AIResponseValidationError
        ):
            calculate_cosine_similarity(
                first=(
                    0.0,
                    0.0,
                ),
                second=(
                    1.0,
                    0.0,
                ),
            )

    def test_score_stays_between_zero_and_100(
        self,
    ):
        values = (
            Decimal("-1"),
            Decimal("-0.5"),
            Decimal("0"),
            Decimal("0.5"),
            Decimal("1"),
        )

        for value in values:
            (
                _,
                score,
            ) = calculate_semantic_alignment(
                cosine_similarity=value
            )

            self.assertGreaterEqual(
                score,
                Decimal("0"),
            )

            self.assertLessEqual(
                score,
                Decimal("100"),
            )

    def test_candidate_module_does_not_import_openai(
        self,
    ):
        candidate_path = (
            Path(__file__)
            .resolve()
            .parent
            / "ai_candidate_1.py"
        )

        source = candidate_path.read_text(
            encoding="utf-8"
        ).lower()

        self.assertNotIn(
            "import openai",
            source,
        )

        self.assertNotIn(
            "from openai",
            source,
        )


class AICandidate1DeterminismTests(
    SimpleTestCase
):
    def test_same_input_returns_same_ranking(
        self,
    ):
        careers = (
            career(
                1,
                "Career A",
                "A",
            ),
            career(
                2,
                "Career B",
                "B",
            ),
        )

        vectors = (
            (
                1.0,
                0.0,
            ),
            (
                0.8,
                0.6,
            ),
            (
                0.6,
                0.8,
            ),
        )

        first = score_ai_candidate_1(
            student_semantic_text="Student",
            careers=careers,
            embedding_provider=(
                FakeEmbeddingProvider(
                    vectors=vectors
                )
            ),
        )

        second = score_ai_candidate_1(
            student_semantic_text="Student",
            careers=careers,
            embedding_provider=(
                FakeEmbeddingProvider(
                    vectors=vectors
                )
            ),
        )

        self.assertEqual(
            first,
            second,
        )
