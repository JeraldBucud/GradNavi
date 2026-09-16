"""
Tests for production GradNavi Technology Fit.

No external services are contacted.
"""

from decimal import Decimal
from pathlib import Path

from django.test import SimpleTestCase

from careers.services.recommendation_scoring import (
    ScoreStatus,
)

from careers.services.technology_fit import (
    TechnologyDemandRequirement,
    TechnologyFitResult,
    TechnologyIdfWeight,
    build_technology_idf_weights,
    calculate_student_technology_signal,
    calculate_technology_fit,
    rank_technology_fit_results,
)

from profiles.models import StudentSkill


FOUNDATIONAL = (
    StudentSkill
    .ProficiencyLevel
    .FOUNDATIONAL
)

DEVELOPING = (
    StudentSkill
    .ProficiencyLevel
    .DEVELOPING
)

PROFICIENT = (
    StudentSkill
    .ProficiencyLevel
    .PROFICIENT
)

ADVANCED = (
    StudentSkill
    .ProficiencyLevel
    .ADVANCED
)


def make_requirement(
    *,
    career_skill_id,
    skill_id,
    skill_name,
    demand_percentage,
):
    return TechnologyDemandRequirement(
        career_skill_id=(
            career_skill_id
        ),
        skill_id=skill_id,
        skill_name=skill_name,
        demand_percentage=Decimal(
            demand_percentage
        ),
    )


def make_weight(
    *,
    skill_id,
    skill_name,
    weight="1",
):
    return TechnologyIdfWeight(
        skill_id=skill_id,
        skill_name=skill_name,
        document_frequency=1,
        supported_career_count=3,
        idf_weight=Decimal(
            weight
        ),
    )


PYTHON = make_requirement(
    career_skill_id=101,
    skill_id=1,
    skill_name="Python",
    demand_percentage="25",
)

REACT = make_requirement(
    career_skill_id=102,
    skill_id=2,
    skill_name="React",
    demand_percentage="75",
)

POSTGRESQL = make_requirement(
    career_skill_id=103,
    skill_id=3,
    skill_name="PostgreSQL",
    demand_percentage="20",
)


REQUIREMENTS = (
    PYTHON,
    REACT,
)


WEIGHTS = {
    1: make_weight(
        skill_id=1,
        skill_name="Python",
    ),

    2: make_weight(
        skill_id=2,
        skill_name="React",
    ),

    3: make_weight(
        skill_id=3,
        skill_name="PostgreSQL",
    ),
}


class TechnologyFitScoringTests(
    SimpleTestCase
):
    def calculate(
        self,
        *,
        proficiencies,
        requirements=REQUIREMENTS,
        weights=WEIGHTS,
    ):
        return calculate_technology_fit(
            career_id=1,
            career_name="Test Career",
            student_proficiencies=(
                proficiencies
            ),
            requirements=(
                requirements
            ),
            idf_weights=(
                weights
            ),
        )

    def test_empty_profile_is_insufficient(
        self,
    ):
        result = self.calculate(
            proficiencies={}
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus
            .INSUFFICIENT_PROFILE,
        )

    def test_missing_evidence_is_insufficient(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
            requirements=(),
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus
            .INSUFFICIENT_EVIDENCE,
        )

    def test_unrecognised_student_signal_is_insufficient(
        self,
    ):
        result = self.calculate(
            proficiencies={
                9999: ADVANCED,
            },
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus
            .INSUFFICIENT_PROFILE,
        )

    def test_no_match_returns_zero(
        self,
    ):
        result = self.calculate(
            proficiencies={
                3: ADVANCED,
            },
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.technology_fit_score,
            Decimal("0.00"),
        )

    def test_full_advanced_match_returns_100(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: ADVANCED,
                2: ADVANCED,
            },
        )

        self.assertEqual(
            result.technology_fit_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.student_alignment_ratio,
            Decimal("1"),
        )

        self.assertEqual(
            result.demand_coverage_ratio,
            Decimal("1"),
        )

    def test_harmonic_mean_known_example(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
        )

        self.assertEqual(
            result.student_alignment_ratio,
            Decimal("1"),
        )

        self.assertEqual(
            result.demand_coverage_ratio,
            Decimal("0.25"),
        )

        self.assertEqual(
            result.technology_fit_score,
            Decimal("40.00"),
        )

    def test_proficiency_increases_score(
        self,
    ):
        foundational = self.calculate(
            proficiencies={
                1: FOUNDATIONAL,
            },
        )

        developing = self.calculate(
            proficiencies={
                1: DEVELOPING,
            },
        )

        proficient = self.calculate(
            proficiencies={
                1: PROFICIENT,
            },
        )

        advanced = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
        )

        scores = (
            foundational.technology_fit_score,
            developing.technology_fit_score,
            proficient.technology_fit_score,
            advanced.technology_fit_score,
        )

        self.assertLess(
            scores[0],
            scores[1],
        )

        self.assertLess(
            scores[1],
            scores[2],
        )

        self.assertLess(
            scores[2],
            scores[3],
        )

    def test_higher_demand_match_scores_higher(
        self,
    ):
        high = (
            make_requirement(
                career_skill_id=201,
                skill_id=1,
                skill_name="Python",
                demand_percentage="75",
            ),
            make_requirement(
                career_skill_id=202,
                skill_id=2,
                skill_name="React",
                demand_percentage="25",
            ),
        )

        low = (
            make_requirement(
                career_skill_id=301,
                skill_id=1,
                skill_name="Python",
                demand_percentage="25",
            ),
            make_requirement(
                career_skill_id=302,
                skill_id=2,
                skill_name="React",
                demand_percentage="75",
            ),
        )

        high_result = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
            requirements=high,
        )

        low_result = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
            requirements=low,
        )

        self.assertGreater(
            high_result.technology_fit_score,
            low_result.technology_fit_score,
        )

    def test_idf_weights_favour_rarer_technology(
        self,
    ):
        requirements = {
            1: (
                make_requirement(
                    career_skill_id=1,
                    skill_id=10,
                    skill_name="Common",
                    demand_percentage="10",
                ),
                make_requirement(
                    career_skill_id=2,
                    skill_id=20,
                    skill_name="Rare",
                    demand_percentage="10",
                ),
            ),
            2: (
                make_requirement(
                    career_skill_id=3,
                    skill_id=10,
                    skill_name="Common",
                    demand_percentage="10",
                ),
            ),
            3: (
                make_requirement(
                    career_skill_id=4,
                    skill_id=10,
                    skill_name="Common",
                    demand_percentage="10",
                ),
            ),
        }

        weights = (
            build_technology_idf_weights(
                requirements_by_career=(
                    requirements
                )
            )
        )

        self.assertGreater(
            weights[20].idf_weight,
            weights[10].idf_weight,
        )

    def test_student_signal_ignores_non_onet_technology(
        self,
    ):
        signal = (
            calculate_student_technology_signal(
                student_proficiencies={
                    1: ADVANCED,
                    999: ADVANCED,
                },
                idf_weights=WEIGHTS,
            )
        )

        self.assertEqual(
            signal,
            Decimal("100"),
        )

    def test_duplicate_requirement_rejected(
        self,
    ):
        duplicate = (
            make_requirement(
                career_skill_id=101,
                skill_id=1,
                skill_name="Python",
                demand_percentage="25",
            ),
            make_requirement(
                career_skill_id=101,
                skill_id=2,
                skill_name="React",
                demand_percentage="75",
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            self.calculate(
                proficiencies={
                    1: ADVANCED,
                    2: ADVANCED,
                },
                requirements=duplicate,
            )

    def test_invalid_percentage_rejected(
        self,
    ):
        invalid = (
            make_requirement(
                career_skill_id=999,
                skill_id=1,
                skill_name="Python",
                demand_percentage="101",
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            self.calculate(
                proficiencies={
                    1: ADVANCED,
                },
                requirements=invalid,
            )

    def test_ranking_uses_fit_then_coverage(
        self,
    ):
        result_a = TechnologyFitResult(
            career_id=1,
            career_name="Career A",
            score_status=(
                ScoreStatus.SCORED
            ),
            technology_fit_score=(
                Decimal("50.00")
            ),
            technology_fit_ratio=(
                Decimal("0.5")
            ),
            student_alignment_ratio=(
                Decimal("0.5")
            ),
            demand_coverage_ratio=(
                Decimal("0.6")
            ),
        )

        result_b = TechnologyFitResult(
            career_id=2,
            career_name="Career B",
            score_status=(
                ScoreStatus.SCORED
            ),
            technology_fit_score=(
                Decimal("50.00")
            ),
            technology_fit_ratio=(
                Decimal("0.5")
            ),
            student_alignment_ratio=(
                Decimal("0.6")
            ),
            demand_coverage_ratio=(
                Decimal("0.5")
            ),
        )

        ranked = (
            rank_technology_fit_results(
                (
                    result_b,
                    result_a,
                )
            )
        )

        self.assertEqual(
            ranked[0].career_id,
            1,
        )

    def test_production_service_does_not_import_experimental_candidates(
        self,
    ):
        service_path = (
            Path(__file__)
            .resolve()
            .parents[1]
            / "services"
            / "technology_fit.py"
        )

        source = (
            service_path
            .read_text(
                encoding="utf-8-sig"
            )
            .casefold()
        )

        self.assertNotIn(
            "scoring_validation."
            "technology_candidate",
            source,
        )
