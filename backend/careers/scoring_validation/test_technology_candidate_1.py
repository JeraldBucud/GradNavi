"""
Unit and property tests for Technology Candidate 1.

Candidate T1 measures Student proficiency across the
occupation-specific technologies marked In Demand by O*NET.

Formula:

    technology_fit =
        sum(student proficiency scores)
        /
        (
            100
            * number of In-Demand technologies
        )
        * 100

Missing technologies contribute zero.

These tests focus on scoring mathematics and deterministic
behaviour. They do not depend on database reference records.
"""

from decimal import Decimal

from django.test import SimpleTestCase

from careers.services.recommendation_scoring import (
    ScoreStatus,
)
from careers.scoring_validation.technology_candidate_1 import (
    TechnologyRequirement,
    calculate_technology_candidate_1_fit,
    rank_technology_candidate_1_results,
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
    hot_technology: bool = True,
) -> TechnologyRequirement:
    """
    Build one deterministic technology requirement.
    """

    return TechnologyRequirement(
        career_skill_id=career_skill_id,
        skill_id=skill_id,
        skill_name=skill_name,
        hot_technology=hot_technology,
    )


REQUIREMENTS = (
    make_requirement(
        career_skill_id=101,
        skill_id=1,
        skill_name="Python",
    ),
    make_requirement(
        career_skill_id=102,
        skill_id=2,
        skill_name="React",
    ),
    make_requirement(
        career_skill_id=103,
        skill_id=3,
        skill_name="PostgreSQL",
    ),
)


class TechnologyCandidate1ScoringTests(
    SimpleTestCase
):
    """
    Behavioural guarantees for Technology Candidate T1.
    """

    def calculate(
        self,
        *,
        proficiencies,
        requirements=REQUIREMENTS,
    ):
        return calculate_technology_candidate_1_fit(
            career_id=1,
            career_name="Test Career",
            student_proficiencies=(
                proficiencies
            ),
            requirements=(
                requirements
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

        self.assertIsNone(
            result.technology_fit_ratio
        )

    def test_missing_career_evidence_is_insufficient_evidence(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: DEVELOPING,
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

    def test_no_matching_technologies_scores_zero(
        self,
    ):
        result = self.calculate(
            proficiencies={
                9999: ADVANCED,
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
            result.technology_fit_ratio,
            Decimal("0"),
        )

        self.assertEqual(
            result.matched_technology_count,
            0,
        )

        self.assertEqual(
            result.missing_technology_count,
            3,
        )

    def test_all_advanced_returns_100_percent(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: ADVANCED,
                2: ADVANCED,
                3: ADVANCED,
            },
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.technology_fit_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.technology_fit_ratio,
            Decimal("1"),
        )

        self.assertEqual(
            result.matched_technology_count,
            3,
        )

        self.assertEqual(
            result.missing_technology_count,
            0,
        )

    def test_known_example_returns_expected_score(
        self,
    ):
        """
        Foundational + Proficient + Advanced:

            25 + 75 + 100
            ----------------
            3 * 100

            = 0.666666...
            = 66.67%
        """

        result = self.calculate(
            proficiencies={
                1: FOUNDATIONAL,
                2: PROFICIENT,
                3: ADVANCED,
            },
        )

        self.assertEqual(
            result.technology_fit_score,
            Decimal("66.67"),
        )

        self.assertEqual(
            result.matched_technology_count,
            3,
        )

    def test_increasing_proficiency_cannot_reduce_score(
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

        self.assertLessEqual(
            scores[0],
            scores[1],
        )

        self.assertLessEqual(
            scores[1],
            scores[2],
        )

        self.assertLessEqual(
            scores[2],
            scores[3],
        )

    def test_adding_matched_technology_cannot_reduce_score(
        self,
    ):
        one_match = self.calculate(
            proficiencies={
                1: PROFICIENT,
            },
        )

        two_matches = self.calculate(
            proficiencies={
                1: PROFICIENT,
                2: PROFICIENT,
            },
        )

        three_matches = self.calculate(
            proficiencies={
                1: PROFICIENT,
                2: PROFICIENT,
                3: PROFICIENT,
            },
        )

        self.assertLessEqual(
            one_match.technology_fit_score,
            two_matches.technology_fit_score,
        )

        self.assertLessEqual(
            two_matches.technology_fit_score,
            three_matches.technology_fit_score,
        )

    def test_score_is_always_bounded_between_zero_and_100(
        self,
    ):
        profiles = (
            {
                9999: ADVANCED,
            },
            {
                1: FOUNDATIONAL,
            },
            {
                1: DEVELOPING,
                2: FOUNDATIONAL,
            },
            {
                1: PROFICIENT,
                2: PROFICIENT,
                3: PROFICIENT,
            },
            {
                1: ADVANCED,
                2: ADVANCED,
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
            1: FOUNDATIONAL,
            2: PROFICIENT,
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
            ),
            make_requirement(
                career_skill_id=101,
                skill_id=2,
                skill_name="React",
            ),
        )

        with self.assertRaises(
            ValueError
        ):
            self.calculate(
                proficiencies={
                    1: DEVELOPING,
                    2: PROFICIENT,
                },
                requirements=(
                    duplicate_requirements
                ),
            )

    def test_matched_and_missing_names_are_recorded(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: FOUNDATIONAL,
                3: ADVANCED,
            },
        )

        self.assertEqual(
            result.matched_technologies,
            (
                "PostgreSQL",
                "Python",
            ),
        )

        self.assertEqual(
            result.missing_technologies,
            (
                "React",
            ),
        )


class TechnologyCandidate1RankingTests(
    SimpleTestCase
):
    """
    Deterministic ranking guarantees for Candidate T1.
    """

    def test_higher_technology_fit_ranks_first(
        self,
    ):
        stronger = (
            calculate_technology_candidate_1_fit(
                career_id=1,
                career_name="Stronger Career",
                student_proficiencies={
                    1: ADVANCED,
                    2: ADVANCED,
                    3: ADVANCED,
                },
                requirements=REQUIREMENTS,
            )
        )

        weaker = (
            calculate_technology_candidate_1_fit(
                career_id=2,
                career_name="Weaker Career",
                student_proficiencies={
                    1: FOUNDATIONAL,
                },
                requirements=REQUIREMENTS,
            )
        )

        ranked = (
            rank_technology_candidate_1_results(
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

        self.assertEqual(
            ranked[1].career_id,
            2,
        )

        self.assertEqual(
            ranked[1].rank,
            2,
        )

    def test_identical_fit_uses_deterministic_name_tiebreak(
        self,
    ):
        profile = {
            1: DEVELOPING,
            2: PROFICIENT,
        }

        alpha = (
            calculate_technology_candidate_1_fit(
                career_id=10,
                career_name="Alpha Career",
                student_proficiencies=profile,
                requirements=REQUIREMENTS,
            )
        )

        beta = (
            calculate_technology_candidate_1_fit(
                career_id=20,
                career_name="Beta Career",
                student_proficiencies=profile,
                requirements=REQUIREMENTS,
            )
        )

        self.assertEqual(
            alpha.technology_fit_ratio,
            beta.technology_fit_ratio,
        )

        ranked = (
            rank_technology_candidate_1_results(
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
        scored = (
            calculate_technology_candidate_1_fit(
                career_id=1,
                career_name="Scored Career",
                student_proficiencies={
                    1: ADVANCED,
                },
                requirements=REQUIREMENTS,
            )
        )

        insufficient = (
            calculate_technology_candidate_1_fit(
                career_id=2,
                career_name="No Evidence Career",
                student_proficiencies={
                    1: ADVANCED,
                },
                requirements=(),
            )
        )

        ranked = (
            rank_technology_candidate_1_results(
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