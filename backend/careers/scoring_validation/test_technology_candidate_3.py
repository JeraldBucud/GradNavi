"""
Unit and property tests for Technology Candidate 3.

Technology Candidate T3 combines:

1. IDF-weighted Student Alignment.
2. O*NET demand-percentage-weighted Career Coverage.
3. Harmonic mean of both signals.

These tests validate scoring mathematics and deterministic
behaviour without depending on database reference records.
"""

from decimal import Decimal

from django.test import SimpleTestCase

from careers.services.recommendation_scoring import (
    ScoreStatus,
)
from careers.scoring_validation.technology_candidate_2 import (
    TechnologyIdfWeight,
)
from careers.scoring_validation.technology_candidate_3 import (
    TechnologyCandidate3Result,
    TechnologyDemandRequirement,
    calculate_technology_candidate_3_fit,
    rank_technology_candidate_3_results,
)
from profiles.models import StudentSkill


FOUNDATIONAL = (
    StudentSkill.ProficiencyLevel.FOUNDATIONAL
)

DEVELOPING = (
    StudentSkill.ProficiencyLevel.DEVELOPING
)

PROFICIENT = (
    StudentSkill.ProficiencyLevel.PROFICIENT
)

ADVANCED = (
    StudentSkill.ProficiencyLevel.ADVANCED
)


def make_requirement(
    *,
    career_skill_id: int,
    skill_id: int,
    skill_name: str,
    demand_percentage: str,
) -> TechnologyDemandRequirement:
    """
    Build one deterministic demand-weighted requirement.
    """

    return TechnologyDemandRequirement(
        career_skill_id=career_skill_id,
        skill_id=skill_id,
        skill_name=skill_name,
        demand_percentage=Decimal(
            demand_percentage
        ),
    )


def make_weight(
    *,
    skill_id: int,
    skill_name: str,
    weight: str = "1",
) -> TechnologyIdfWeight:
    """
    Build one deterministic IDF weight.
    """

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


IDF_WEIGHTS = {
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


class TechnologyCandidate3ScoringTests(
    SimpleTestCase
):
    """
    Behavioural guarantees for Technology Candidate T3.
    """

    def calculate(
        self,
        *,
        proficiencies,
        requirements=REQUIREMENTS,
        weights=IDF_WEIGHTS,
    ):
        return calculate_technology_candidate_3_fit(
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

    def test_empty_student_profile_is_insufficient_profile(
        self,
    ):
        result = self.calculate(
            proficiencies={},
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.INSUFFICIENT_PROFILE,
        )

        self.assertIsNone(
            result.technology_fit_score
        )

    def test_unrecognised_student_profile_is_insufficient_profile(
        self,
    ):
        result = self.calculate(
            proficiencies={
                9999: ADVANCED,
            },
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.INSUFFICIENT_PROFILE,
        )

        self.assertIsNone(
            result.technology_fit_score
        )

    def test_missing_career_evidence_is_insufficient_evidence(
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
            ScoreStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            result.technology_fit_score
        )

    def test_zero_total_demand_is_insufficient_evidence(
        self,
    ):
        zero_requirement = (
            make_requirement(
                career_skill_id=201,
                skill_id=1,
                skill_name="Python",
                demand_percentage="0",
            ),
        )

        result = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
            requirements=(
                zero_requirement
            ),
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.INSUFFICIENT_EVIDENCE,
        )

        self.assertIsNone(
            result.technology_fit_score
        )

    def test_no_matching_technology_scores_zero(
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

        self.assertEqual(
            result.student_alignment_ratio,
            Decimal("0"),
        )

        self.assertEqual(
            result.demand_coverage_ratio,
            Decimal("0"),
        )

    def test_all_requirements_advanced_returns_100_percent(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: ADVANCED,
                2: ADVANCED,
            },
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.student_alignment_ratio,
            Decimal("1"),
        )

        self.assertEqual(
            result.demand_coverage_ratio,
            Decimal("1"),
        )

        self.assertEqual(
            result.technology_fit_ratio,
            Decimal("1"),
        )

        self.assertEqual(
            result.technology_fit_score,
            Decimal("100.00"),
        )

    def test_known_harmonic_mean_example_returns_40_percent(
        self,
    ):
        """
        Student has only Python.

        Python demand = 25
        React demand = 75

        Student Alignment:
            100%

        Demand Coverage:
            25 / 100
            = 25%

        Harmonic mean:

            2 * 1.00 * 0.25
            ----------------
                1.00 + 0.25

            = 0.40
            = 40%
        """

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

    def test_increasing_matched_proficiency_increases_fit(
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

    def test_higher_demand_matched_skill_produces_higher_fit(
        self,
    ):
        high_demand_match = (
            (
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
        )

        low_demand_match = (
            (
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
        )

        high_result = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
            requirements=(
                high_demand_match
            ),
        )

        low_result = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
            requirements=(
                low_demand_match
            ),
        )

        self.assertGreater(
            high_result.demand_coverage_ratio,
            low_result.demand_coverage_ratio,
        )

        self.assertGreater(
            high_result.technology_fit_score,
            low_result.technology_fit_score,
        )

    def test_unmatched_recognised_technology_reduces_fit(
        self,
    ):
        matched_only = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
        )

        with_unmatched = self.calculate(
            proficiencies={
                1: ADVANCED,
                3: ADVANCED,
            },
        )

        self.assertGreater(
            matched_only.student_alignment_ratio,
            with_unmatched.student_alignment_ratio,
        )

        self.assertGreater(
            matched_only.technology_fit_score,
            with_unmatched.technology_fit_score,
        )

    def test_demand_coverage_uses_student_proficiency(
        self,
    ):
        foundational = self.calculate(
            proficiencies={
                1: FOUNDATIONAL,
            },
        )

        advanced = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
        )

        self.assertLess(
            foundational.demand_coverage_ratio,
            advanced.demand_coverage_ratio,
        )

    def test_score_stays_between_zero_and_100(
        self,
    ):
        profiles = (
            {
                1: FOUNDATIONAL,
            },
            {
                1: DEVELOPING,
            },
            {
                1: PROFICIENT,
                3: ADVANCED,
            },
            {
                1: ADVANCED,
                2: ADVANCED,
            },
            {
                3: ADVANCED,
            },
        )

        for profile in profiles:
            with self.subTest(
                profile=profile
            ):
                result = self.calculate(
                    proficiencies=profile
                )

                self.assertEqual(
                    result.score_status,
                    ScoreStatus.SCORED,
                )

                self.assertGreaterEqual(
                    result.technology_fit_score,
                    Decimal("0"),
                )

                self.assertLessEqual(
                    result.technology_fit_score,
                    Decimal("100"),
                )

    def test_same_input_is_deterministic(
        self,
    ):
        profile = {
            1: PROFICIENT,
            2: FOUNDATIONAL,
            3: ADVANCED,
        }

        first = self.calculate(
            proficiencies=profile
        )

        second = self.calculate(
            proficiencies=profile
        )

        self.assertEqual(
            first,
            second,
        )

    def test_duplicate_requirement_is_rejected(
        self,
    ):
        duplicate_requirements = (
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
                requirements=(
                    duplicate_requirements
                ),
            )

    def test_missing_idf_weight_is_rejected(
        self,
    ):
        incomplete_weights = {
            1: IDF_WEIGHTS[1],
        }

        with self.assertRaises(
            ValueError
        ):
            self.calculate(
                proficiencies={
                    1: ADVANCED,
                },
                weights=(
                    incomplete_weights
                ),
            )

    def test_invalid_demand_percentage_is_rejected(
        self,
    ):
        invalid_requirements = (
            make_requirement(
                career_skill_id=201,
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
                requirements=(
                    invalid_requirements
                ),
            )

    def test_matched_and_missing_names_are_recorded(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: ADVANCED,
            },
        )

        self.assertEqual(
            result.matched_technologies,
            (
                "Python",
            ),
        )

        self.assertEqual(
            result.missing_technologies,
            (
                "React",
            ),
        )

        self.assertEqual(
            result.matched_technology_count,
            1,
        )

        self.assertEqual(
            result.missing_technology_count,
            1,
        )


class TechnologyCandidate3RankingTests(
    SimpleTestCase
):
    """
    Deterministic ranking guarantees for Technology Candidate T3.
    """

    def make_result(
        self,
        *,
        career_id,
        career_name,
        fit,
        coverage,
        alignment,
        matched_demand,
    ):
        return TechnologyCandidate3Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.SCORED
            ),
            technology_fit_score=(
                fit
                * Decimal("100")
            ).quantize(
                Decimal("0.01")
            ),
            technology_fit_ratio=fit,
            demand_coverage_ratio=coverage,
            student_alignment_ratio=alignment,
            matched_demand_signal=(
                matched_demand
            ),
            matched_student_signal=(
                Decimal("1")
            ),
            student_signal=(
                Decimal("1")
            ),
            total_demand_signal=(
                Decimal("1")
            ),
        )

    def test_higher_technology_fit_ranks_first(
        self,
    ):
        stronger = self.make_result(
            career_id=1,
            career_name="Stronger Career",
            fit=Decimal("0.8"),
            coverage=Decimal("0.8"),
            alignment=Decimal("0.8"),
            matched_demand=Decimal("80"),
        )

        weaker = self.make_result(
            career_id=2,
            career_name="Weaker Career",
            fit=Decimal("0.4"),
            coverage=Decimal("0.4"),
            alignment=Decimal("0.4"),
            matched_demand=Decimal("40"),
        )

        ranked = (
            rank_technology_candidate_3_results(
                (
                    weaker,
                    stronger,
                )
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

    def test_same_fit_uses_higher_demand_coverage(
        self,
    ):
        higher_coverage = self.make_result(
            career_id=1,
            career_name="Higher Coverage",
            fit=Decimal("0.5"),
            coverage=Decimal("0.7"),
            alignment=Decimal("0.4"),
            matched_demand=Decimal("70"),
        )

        lower_coverage = self.make_result(
            career_id=2,
            career_name="Lower Coverage",
            fit=Decimal("0.5"),
            coverage=Decimal("0.5"),
            alignment=Decimal("0.8"),
            matched_demand=Decimal("50"),
        )

        ranked = (
            rank_technology_candidate_3_results(
                (
                    lower_coverage,
                    higher_coverage,
                )
            )
        )

        self.assertEqual(
            ranked[0].career_id,
            1,
        )

    def test_identical_metrics_use_name_tiebreak(
        self,
    ):
        alpha = self.make_result(
            career_id=10,
            career_name="Alpha Career",
            fit=Decimal("0.5"),
            coverage=Decimal("0.5"),
            alignment=Decimal("0.5"),
            matched_demand=Decimal("50"),
        )

        beta = self.make_result(
            career_id=20,
            career_name="Beta Career",
            fit=Decimal("0.5"),
            coverage=Decimal("0.5"),
            alignment=Decimal("0.5"),
            matched_demand=Decimal("50"),
        )

        ranked = (
            rank_technology_candidate_3_results(
                (
                    beta,
                    alpha,
                )
            )
        )

        self.assertEqual(
            ranked[0].career_name,
            "Alpha Career",
        )

        self.assertEqual(
            ranked[1].career_name,
            "Beta Career",
        )

    def test_unscored_result_is_not_ranked(
        self,
    ):
        scored = self.make_result(
            career_id=1,
            career_name="Scored Career",
            fit=Decimal("0.5"),
            coverage=Decimal("0.5"),
            alignment=Decimal("0.5"),
            matched_demand=Decimal("50"),
        )

        insufficient = (
            TechnologyCandidate3Result(
                career_id=2,
                career_name="No Evidence Career",
                score_status=(
                    ScoreStatus.INSUFFICIENT_EVIDENCE
                ),
            )
        )

        ranked = (
            rank_technology_candidate_3_results(
                (
                    insufficient,
                    scored,
                )
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
            ranked[1].career_id,
            2,
        )

        self.assertIsNone(
            ranked[1].rank
        )

        self.assertEqual(
            ranked[1].score_status,
            ScoreStatus.INSUFFICIENT_EVIDENCE,
        )
