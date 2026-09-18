"""
Tests for the locked WBS 5.3 composite recommendation service.

No database writes.
No external AI provider requests.
"""

from decimal import Decimal
from pathlib import Path

from django.test import SimpleTestCase

from careers.services.ai_semantic_alignment import (
    SemanticAlignmentContextMode,
    SemanticAlignmentResult,
)

from careers.services.composite_recommendation import (
    COMPETENCY_WEIGHT,
    SEMANTIC_WEIGHT,
    TECHNOLOGY_ALIGNMENT_THRESHOLD,
    TECHNOLOGY_WEIGHT,
    build_composite_results,
    calculate_composite_score,
    min_max_normalize_scores,
    technology_component_is_active,
)

from careers.services.recommendation_scoring import (
    RecommendationResult,
    ScoreStatus,
)

from careers.services.technology_fit import (
    TechnologyFitResult,
)


def competency_result(
    *,
    career_id,
    career_name,
    score,
    status=ScoreStatus.SCORED,
):
    return RecommendationResult(
        career_id=career_id,
        career_name=career_name,
        score_status=status,
        recommendation_score=score,
    )


def technology_result(
    *,
    career_id,
    career_name,
    score,
    alignment,
    status=ScoreStatus.SCORED,
):
    return TechnologyFitResult(
        career_id=career_id,
        career_name=career_name,
        score_status=status,
        technology_fit_score=score,
        technology_fit_ratio=(
            score / Decimal("100")
            if score is not None
            else None
        ),
        student_alignment_ratio=alignment,
        demand_coverage_ratio=alignment,
    )


def semantic_result(
    *,
    career_id,
    career_name,
    score,
):
    return SemanticAlignmentResult(
        career_id=career_id,
        career_name=career_name,
        semantic_alignment_score=score,
        semantic_alignment_ratio=(
            score
            / Decimal("100")
        ),
        identity_similarity=(
            score
            / Decimal("100")
        ),
        esco_similarity=None,
        context_mode=(
            SemanticAlignmentContextMode
            .IDENTITY_ONLY
        ),
        essential_esco_count=0,
    )


class CompositeRecommendationTests(
    SimpleTestCase
):
    def test_locked_weights(
        self,
    ):
        self.assertEqual(
            COMPETENCY_WEIGHT,
            Decimal("0.20"),
        )

        self.assertEqual(
            TECHNOLOGY_WEIGHT,
            Decimal("0.20"),
        )

        self.assertEqual(
            SEMANTIC_WEIGHT,
            Decimal("0.60"),
        )

        self.assertEqual(
            TECHNOLOGY_ALIGNMENT_THRESHOLD,
            Decimal("0.10"),
        )

    def test_min_max_normalization(
        self,
    ):
        normalized = (
            min_max_normalize_scores(
                {
                    1: Decimal("10"),
                    2: Decimal("20"),
                    3: Decimal("15"),
                    4: None,
                }
            )
        )

        self.assertEqual(
            normalized[1],
            Decimal("0.000000"),
        )

        self.assertEqual(
            normalized[2],
            Decimal("100.000000"),
        )

        self.assertEqual(
            normalized[3],
            Decimal("50.000000"),
        )

        self.assertIsNone(
            normalized[4]
        )

    def test_equal_scores_have_no_discrimination(
        self,
    ):
        normalized = (
            min_max_normalize_scores(
                {
                    1: Decimal("25"),
                    2: Decimal("25"),
                }
            )
        )

        self.assertEqual(
            normalized[1],
            Decimal("0"),
        )

        self.assertEqual(
            normalized[2],
            Decimal("0"),
        )

    def test_technology_threshold_boundary_is_active(
        self,
    ):
        result = technology_result(
            career_id=1,
            career_name="Career A",
            score=Decimal("25"),
            alignment=Decimal("0.10"),
        )

        self.assertTrue(
            technology_component_is_active(
                result
            )
        )

    def test_technology_below_threshold_is_inactive(
        self,
    ):
        result = technology_result(
            career_id=1,
            career_name="Career A",
            score=Decimal("25"),
            alignment=Decimal("0.099999"),
        )

        self.assertFalse(
            technology_component_is_active(
                result
            )
        )

    def test_unscored_technology_is_inactive(
        self,
    ):
        result = technology_result(
            career_id=1,
            career_name="Career A",
            score=None,
            alignment=None,
            status=(
                ScoreStatus
                .INSUFFICIENT_EVIDENCE
            ),
        )

        self.assertFalse(
            technology_component_is_active(
                result
            )
        )

    def test_all_components_use_locked_weights(
        self,
    ):
        (
            score,
            weights,
        ) = calculate_composite_score(
            competency_normalized=(
                Decimal("40")
            ),
            technology_normalized=(
                Decimal("80")
            ),
            semantic_normalized=(
                Decimal("100")
            ),
            technology_active=True,
        )

        self.assertEqual(
            score,
            Decimal("84.00"),
        )

        self.assertEqual(
            weights.competency,
            Decimal("0.20"),
        )

        self.assertEqual(
            weights.technology,
            Decimal("0.20"),
        )

        self.assertEqual(
            weights.semantic,
            Decimal("0.60"),
        )

    def test_missing_technology_weight_is_redistributed(
        self,
    ):
        (
            score,
            weights,
        ) = calculate_composite_score(
            competency_normalized=(
                Decimal("40")
            ),
            technology_normalized=(
                Decimal("80")
            ),
            semantic_normalized=(
                Decimal("100")
            ),
            technology_active=False,
        )

        self.assertEqual(
            score,
            Decimal("85.00"),
        )

        self.assertEqual(
            weights.competency,
            Decimal("0.25"),
        )

        self.assertEqual(
            weights.technology,
            Decimal("0"),
        )

        self.assertEqual(
            weights.semantic,
            Decimal("0.75"),
        )

    def test_missing_competency_weight_is_redistributed(
        self,
    ):
        (
            score,
            weights,
        ) = calculate_composite_score(
            competency_normalized=None,
            technology_normalized=(
                Decimal("40")
            ),
            semantic_normalized=(
                Decimal("100")
            ),
            technology_active=True,
        )

        self.assertEqual(
            score,
            Decimal("85.00"),
        )

        self.assertEqual(
            weights.competency,
            Decimal("0"),
        )

        self.assertEqual(
            weights.technology,
            Decimal("0.25"),
        )

        self.assertEqual(
            weights.semantic,
            Decimal("0.75"),
        )

    def test_semantic_only_receives_full_weight(
        self,
    ):
        (
            score,
            weights,
        ) = calculate_composite_score(
            competency_normalized=None,
            technology_normalized=None,
            semantic_normalized=(
                Decimal("72")
            ),
            technology_active=False,
        )

        self.assertEqual(
            score,
            Decimal("72.00"),
        )

        self.assertEqual(
            weights.semantic,
            Decimal("1"),
        )

    def test_composite_ranking_uses_normalized_components(
        self,
    ):
        competency = (
            competency_result(
                career_id=1,
                career_name="Career A",
                score=Decimal("10"),
            ),
            competency_result(
                career_id=2,
                career_name="Career B",
                score=Decimal("20"),
            ),
        )

        technology = (
            technology_result(
                career_id=1,
                career_name="Career A",
                score=Decimal("10"),
                alignment=Decimal("0.20"),
            ),
            technology_result(
                career_id=2,
                career_name="Career B",
                score=Decimal("20"),
                alignment=Decimal("0.20"),
            ),
        )

        semantic = (
            semantic_result(
                career_id=1,
                career_name="Career A",
                score=Decimal("20"),
            ),
            semantic_result(
                career_id=2,
                career_name="Career B",
                score=Decimal("10"),
            ),
        )

        results = (
            build_composite_results(
                competency_results=(
                    competency
                ),
                technology_results=(
                    technology
                ),
                semantic_results=(
                    semantic
                ),
            )
        )

        self.assertEqual(
            results[0].career_name,
            "Career A",
        )

        self.assertEqual(
            results[0].recommendation_score,
            Decimal("60.00"),
        )

        self.assertEqual(
            results[1].career_name,
            "Career B",
        )

        self.assertEqual(
            results[1].recommendation_score,
            Decimal("40.00"),
        )

    def test_low_alignment_removes_technology_component(
        self,
    ):
        competency = (
            competency_result(
                career_id=1,
                career_name="Career A",
                score=Decimal("50"),
            ),
            competency_result(
                career_id=2,
                career_name="Career B",
                score=Decimal("0"),
            ),
        )

        technology = (
            technology_result(
                career_id=1,
                career_name="Career A",
                score=Decimal("100"),
                alignment=Decimal("0.09"),
            ),
            technology_result(
                career_id=2,
                career_name="Career B",
                score=Decimal("0"),
                alignment=Decimal("0.20"),
            ),
        )

        semantic = (
            semantic_result(
                career_id=1,
                career_name="Career A",
                score=Decimal("100"),
            ),
            semantic_result(
                career_id=2,
                career_name="Career B",
                score=Decimal("0"),
            ),
        )

        results = (
            build_composite_results(
                competency_results=(
                    competency
                ),
                technology_results=(
                    technology
                ),
                semantic_results=(
                    semantic
                ),
            )
        )

        career_a = next(
            result
            for result
            in results
            if result.career_id == 1
        )

        self.assertFalse(
            career_a.technology_active
        )

        self.assertEqual(
            career_a
            .effective_technology_weight,
            Decimal("0"),
        )

        self.assertEqual(
            career_a
            .effective_competency_weight,
            Decimal("0.25"),
        )

        self.assertEqual(
            career_a
            .effective_semantic_weight,
            Decimal("0.75"),
        )

    def test_mismatched_component_career_sets_are_rejected(
        self,
    ):
        competency = (
            competency_result(
                career_id=1,
                career_name="Career A",
                score=Decimal("10"),
            ),
        )

        technology = (
            technology_result(
                career_id=2,
                career_name="Career B",
                score=Decimal("10"),
                alignment=Decimal("0.20"),
            ),
        )

        semantic = (
            semantic_result(
                career_id=1,
                career_name="Career A",
                score=Decimal("10"),
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            build_composite_results(
                competency_results=(
                    competency
                ),
                technology_results=(
                    technology
                ),
                semantic_results=(
                    semantic
                ),
            )

    def test_production_service_stays_provider_independent(
        self,
    ):
        service_path = (
            Path(__file__)
            .resolve()
            .parents[1]
            / "services"
            / "composite_recommendation.py"
        )

        source = (
            service_path
            .read_text(
                encoding="utf-8-sig"
            )
            .casefold()
        )

        self.assertNotIn(
            "openai_embeddings",
            source,
        )

        self.assertIn(
            "embeddingprovider",
            source,
        )
