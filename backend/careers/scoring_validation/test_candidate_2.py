"""
Unit and property tests for Candidate 2 Career Fit scoring.

Candidate 2 is the selected experimental competency component:

    deficit_i =
        max(
            required_level_i - student_score_i,
            0
        )

    weighted_distance =
        sqrt(
            sum(
                importance_i * deficit_i^2
            )
        )

    maximum_distance =
        sqrt(
            sum(
                importance_i * required_level_i^2
            )
        )

    career_fit =
        (
            1
            - weighted_distance / maximum_distance
        ) * 100

These tests intentionally avoid reference-dataset database records.
They validate the behaviour of the scoring mathematics itself.
"""

from decimal import Decimal

from django.test import SimpleTestCase

from careers.services.recommendation_scoring import (
    ScoreStatus,
)
from careers.services.readiness_scoring import (
    CareerReadinessRequirement,
)
from careers.scoring_validation.candidate_2 import (
    calculate_candidate_2_fit,
    rank_candidate_2_results,
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
    importance: str,
    required_level: str,
) -> CareerReadinessRequirement:
    """
    Build one deterministic test requirement.
    """

    return CareerReadinessRequirement(
        career_skill_id=career_skill_id,
        skill_id=skill_id,
        skill_name=skill_name,
        concept_type="skill",
        source_domain="onet_essential_skills",
        importance=Decimal(
            importance
        ),
        required_level=Decimal(
            required_level
        ),
    )


REQUIREMENTS = (
    make_requirement(
        career_skill_id=101,
        skill_id=1,
        skill_name="Programming",
        importance="90",
        required_level="50",
    ),
    make_requirement(
        career_skill_id=102,
        skill_id=2,
        skill_name="Critical Thinking",
        importance="80",
        required_level="75",
    ),
    make_requirement(
        career_skill_id=103,
        skill_id=3,
        skill_name="Systems Analysis",
        importance="70",
        required_level="50",
    ),
)


class Candidate2ScoringTests(
    SimpleTestCase
):
    """
    Behavioural guarantees for Candidate 2.
    """

    def calculate(
        self,
        *,
        proficiencies,
        requirements=REQUIREMENTS,
    ):
        return calculate_candidate_2_fit(
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
            result.career_fit_score
        )

        self.assertIsNone(
            result.normalized_deficit
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
            result.career_fit_score
        )

    def test_meeting_every_requirement_returns_100_percent(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: DEVELOPING,
                2: PROFICIENT,
                3: DEVELOPING,
            }
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.career_fit_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.normalized_deficit,
            Decimal("0"),
        )

        self.assertEqual(
            result.missing_requirement_count,
            0,
        )

    def test_exceeding_requirements_does_not_reduce_score(
        self,
    ):
        meets_requirements = (
            self.calculate(
                proficiencies={
                    1: DEVELOPING,
                    2: PROFICIENT,
                    3: DEVELOPING,
                }
            )
        )

        exceeds_requirements = (
            self.calculate(
                proficiencies={
                    1: ADVANCED,
                    2: ADVANCED,
                    3: ADVANCED,
                }
            )
        )

        self.assertEqual(
            meets_requirements.career_fit_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            exceeds_requirements.career_fit_score,
            Decimal("100.00"),
        )

    def test_increasing_proficiency_cannot_reduce_score(
        self,
    ):
        foundational = self.calculate(
            proficiencies={
                1: FOUNDATIONAL,
                2: FOUNDATIONAL,
                3: FOUNDATIONAL,
            }
        )

        developing = self.calculate(
            proficiencies={
                1: DEVELOPING,
                2: DEVELOPING,
                3: DEVELOPING,
            }
        )

        proficient = self.calculate(
            proficiencies={
                1: PROFICIENT,
                2: PROFICIENT,
                3: PROFICIENT,
            }
        )

        advanced = self.calculate(
            proficiencies={
                1: ADVANCED,
                2: ADVANCED,
                3: ADVANCED,
            }
        )

        scores = (
            foundational.career_fit_score,
            developing.career_fit_score,
            proficient.career_fit_score,
            advanced.career_fit_score,
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

    def test_removing_matched_competency_cannot_improve_score(
        self,
    ):
        more_complete = self.calculate(
            proficiencies={
                1: DEVELOPING,
                2: PROFICIENT,
                3: DEVELOPING,
            }
        )

        less_complete = self.calculate(
            proficiencies={
                1: DEVELOPING,
                2: PROFICIENT,
            }
        )

        self.assertGreaterEqual(
            more_complete.career_fit_score,
            less_complete.career_fit_score,
        )

    def test_student_with_only_unrelated_skill_scores_zero(
        self,
    ):
        result = self.calculate(
            proficiencies={
                9999: ADVANCED,
            }
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.career_fit_score,
            Decimal("0.00"),
        )

        self.assertEqual(
            result.normalized_deficit,
            Decimal("1"),
        )

        self.assertEqual(
            result.matched_requirement_count,
            0,
        )

        self.assertEqual(
            result.missing_requirement_count,
            3,
        )

    def test_partial_profile_produces_score_between_zero_and_100(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: DEVELOPING,
            }
        )

        self.assertGreater(
            result.career_fit_score,
            Decimal("0"),
        )

        self.assertLess(
            result.career_fit_score,
            Decimal("100"),
        )

    def test_score_is_always_bounded_between_zero_and_100(
        self,
    ):
        profiles = (
            {
                999: ADVANCED,
            },
            {
                1: FOUNDATIONAL,
            },
            {
                1: DEVELOPING,
                2: FOUNDATIONAL,
            },
            {
                1: DEVELOPING,
                2: PROFICIENT,
                3: DEVELOPING,
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
                    result.career_fit_score,
                    Decimal("0"),
                )

                self.assertLessEqual(
                    result.career_fit_score,
                    Decimal("100"),
                )

    def test_same_input_is_deterministic(
        self,
    ):
        profile = {
            1: DEVELOPING,
            2: FOUNDATIONAL,
            3: PROFICIENT,
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

    def test_duplicate_career_skill_requirement_is_rejected(
        self,
    ):
        duplicate_requirements = (
            make_requirement(
                career_skill_id=101,
                skill_id=1,
                skill_name="Programming",
                importance="90",
                required_level="50",
            ),
            make_requirement(
                career_skill_id=101,
                skill_id=2,
                skill_name="Critical Thinking",
                importance="80",
                required_level="75",
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

    def test_large_deficit_is_penalized_more_than_small_deficit(
        self,
    ):
        """
        Candidate 2 intentionally squares deficits.

        A student far below a requirement should therefore be
        penalized more strongly than a student only slightly below.
        """

        far_below = self.calculate(
            proficiencies={
                1: FOUNDATIONAL,
                2: FOUNDATIONAL,
                3: FOUNDATIONAL,
            }
        )

        closer = self.calculate(
            proficiencies={
                1: DEVELOPING,
                2: DEVELOPING,
                3: DEVELOPING,
            }
        )

        self.assertLess(
            far_below.career_fit_score,
            closer.career_fit_score,
        )


class Candidate2RankingTests(
    SimpleTestCase
):
    """
    Deterministic ranking guarantees.
    """

    def test_higher_fit_ranks_first(
        self,
    ):
        stronger = (
            calculate_candidate_2_fit(
                career_id=1,
                career_name="Stronger Career",
                student_proficiencies={
                    1: DEVELOPING,
                    2: PROFICIENT,
                    3: DEVELOPING,
                },
                requirements=REQUIREMENTS,
            )
        )

        weaker = (
            calculate_candidate_2_fit(
                career_id=2,
                career_name="Weaker Career",
                student_proficiencies={
                    1: FOUNDATIONAL,
                    2: FOUNDATIONAL,
                    3: FOUNDATIONAL,
                },
                requirements=REQUIREMENTS,
            )
        )

        ranked = (
            rank_candidate_2_results(
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

    def test_identical_evidence_uses_deterministic_name_tiebreak(
        self,
    ):
        profile = {
            1: DEVELOPING,
            2: PROFICIENT,
            3: DEVELOPING,
        }

        alpha = (
            calculate_candidate_2_fit(
                career_id=10,
                career_name="Alpha Career",
                student_proficiencies=profile,
                requirements=REQUIREMENTS,
            )
        )

        beta = (
            calculate_candidate_2_fit(
                career_id=20,
                career_name="Beta Career",
                student_proficiencies=profile,
                requirements=REQUIREMENTS,
            )
        )

        self.assertEqual(
            alpha.normalized_deficit,
            beta.normalized_deficit,
        )

        ranked = (
            rank_candidate_2_results(
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