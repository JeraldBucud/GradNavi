"""
Unit and property tests for Technology Candidate 2.

Technology Candidate T2 is Student-centred.

It measures how much of the Student's globally recognised
In-Demand technology signal supports a Career.

These tests validate:

- status handling;
- IDF behaviour;
- Student proficiency;
- partial and complete alignment;
- score bounds;
- deterministic behaviour;
- duplicate protection;
- deterministic ranking.

The tests do not require database reference records.
"""

from decimal import Decimal

from django.test import SimpleTestCase

from careers.services.recommendation_scoring import (
    ScoreStatus,
)
from careers.scoring_validation.technology_candidate_1 import (
    TechnologyRequirement,
)
from careers.scoring_validation.technology_candidate_2 import (
    TechnologyCandidate2Result,
    TechnologyIdfWeight,
    build_technology_idf_weights,
    calculate_student_technology_signal,
    calculate_technology_candidate_2_fit,
    rank_technology_candidate_2_results,
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
) -> TechnologyRequirement:
    """
    Build one deterministic In-Demand technology requirement.
    """

    return TechnologyRequirement(
        career_skill_id=career_skill_id,
        skill_id=skill_id,
        skill_name=skill_name,
        hot_technology=True,
    )


def make_weight(
    *,
    skill_id: int,
    skill_name: str,
    weight: str,
    document_frequency: int = 1,
    supported_career_count: int = 3,
) -> TechnologyIdfWeight:
    """
    Build one deterministic IDF weight.
    """

    return TechnologyIdfWeight(
        skill_id=skill_id,
        skill_name=skill_name,
        document_frequency=document_frequency,
        supported_career_count=supported_career_count,
        idf_weight=Decimal(weight),
    )


PYTHON = make_requirement(
    career_skill_id=101,
    skill_id=1,
    skill_name="Python",
)

REACT = make_requirement(
    career_skill_id=102,
    skill_id=2,
    skill_name="React",
)

POSTGRESQL = make_requirement(
    career_skill_id=103,
    skill_id=3,
    skill_name="PostgreSQL",
)


SOFTWARE_REQUIREMENTS = (
    PYTHON,
    REACT,
)


IDF_WEIGHTS = {
    1: make_weight(
        skill_id=1,
        skill_name="Python",
        weight="1",
    ),
    2: make_weight(
        skill_id=2,
        skill_name="React",
        weight="2",
    ),
    3: make_weight(
        skill_id=3,
        skill_name="PostgreSQL",
        weight="3",
    ),
}


class TechnologyCandidate2WeightTests(
    SimpleTestCase
):
    """
    Tests for the global IDF-style technology weights.
    """

    def test_rarer_technology_receives_higher_weight(
        self,
    ):
        requirements_by_career = {
            1: (
                make_requirement(
                    career_skill_id=101,
                    skill_id=1,
                    skill_name="Common Tech",
                ),
                make_requirement(
                    career_skill_id=102,
                    skill_id=2,
                    skill_name="Rare Tech",
                ),
            ),
            2: (
                make_requirement(
                    career_skill_id=201,
                    skill_id=1,
                    skill_name="Common Tech",
                ),
            ),
            3: (
                make_requirement(
                    career_skill_id=301,
                    skill_id=1,
                    skill_name="Common Tech",
                ),
            ),
        }

        weights = build_technology_idf_weights(
            requirements_by_career=(
                requirements_by_career
            )
        )

        self.assertEqual(
            weights[1].document_frequency,
            3,
        )

        self.assertEqual(
            weights[2].document_frequency,
            1,
        )

        self.assertGreater(
            weights[2].idf_weight,
            weights[1].idf_weight,
        )

    def test_empty_evidence_returns_no_weights(
        self,
    ):
        weights = build_technology_idf_weights(
            requirements_by_career={}
        )

        self.assertEqual(
            weights,
            {},
        )


class TechnologyCandidate2SignalTests(
    SimpleTestCase
):
    """
    Tests for Student technology signal calculation.
    """

    def test_unrecognised_student_skill_is_ignored(
        self,
    ):
        signal = calculate_student_technology_signal(
            student_proficiencies={
                9999: ADVANCED,
            },
            idf_weights=IDF_WEIGHTS,
        )

        self.assertEqual(
            signal,
            Decimal("0"),
        )

    def test_proficiency_affects_student_signal(
        self,
    ):
        foundational = (
            calculate_student_technology_signal(
                student_proficiencies={
                    1: FOUNDATIONAL,
                },
                idf_weights=IDF_WEIGHTS,
            )
        )

        advanced = (
            calculate_student_technology_signal(
                student_proficiencies={
                    1: ADVANCED,
                },
                idf_weights=IDF_WEIGHTS,
            )
        )

        self.assertLess(
            foundational,
            advanced,
        )


class TechnologyCandidate2ScoringTests(
    SimpleTestCase
):
    """
    Behavioural guarantees for Technology Candidate T2.
    """

    def calculate(
        self,
        *,
        proficiencies,
        requirements=SOFTWARE_REQUIREMENTS,
        weights=IDF_WEIGHTS,
    ):
        return calculate_technology_candidate_2_fit(
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
            result.technology_alignment_score
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
            result.technology_alignment_score
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
            result.technology_alignment_score
        )

    def test_all_student_signal_matching_career_returns_100_percent(
        self,
    ):
        result = self.calculate(
            proficiencies={
                1: FOUNDATIONAL,
                2: PROFICIENT,
            },
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertEqual(
            result.technology_alignment_score,
            Decimal("100.00"),
        )

        self.assertEqual(
            result.alignment_ratio,
            Decimal("1"),
        )

    def test_unmatched_recognised_technology_reduces_alignment(
        self,
    ):
        """
        PostgreSQL contributes to the Student signal but is not
        part of SOFTWARE_REQUIREMENTS.

        Therefore alignment must be below 100%.
        """

        result = self.calculate(
            proficiencies={
                1: ADVANCED,
                3: ADVANCED,
            },
        )

        self.assertEqual(
            result.score_status,
            ScoreStatus.SCORED,
        )

        self.assertGreater(
            result.technology_alignment_score,
            Decimal("0"),
        )

        self.assertLess(
            result.technology_alignment_score,
            Decimal("100"),
        )

    def test_no_matching_career_technology_scores_zero(
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
            result.technology_alignment_score,
            Decimal("0.00"),
        )

        self.assertEqual(
            result.matched_technology_count,
            0,
        )

    def test_increasing_matched_proficiency_increases_alignment(
        self,
    ):
        foundational = self.calculate(
            proficiencies={
                1: FOUNDATIONAL,
                3: ADVANCED,
            },
        )

        advanced = self.calculate(
            proficiencies={
                1: ADVANCED,
                3: ADVANCED,
            },
        )

        self.assertLess(
            foundational.technology_alignment_score,
            advanced.technology_alignment_score,
        )

    def test_increasing_unmatched_proficiency_reduces_alignment(
        self,
    ):
        lower_unmatched = self.calculate(
            proficiencies={
                1: ADVANCED,
                3: FOUNDATIONAL,
            },
        )

        higher_unmatched = self.calculate(
            proficiencies={
                1: ADVANCED,
                3: ADVANCED,
            },
        )

        self.assertGreater(
            lower_unmatched.technology_alignment_score,
            higher_unmatched.technology_alignment_score,
        )

    def test_score_stays_between_zero_and_100(
        self,
    ):
        profiles = (
            {
                1: FOUNDATIONAL,
            },
            {
                1: ADVANCED,
            },
            {
                1: DEVELOPING,
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

                self.assertGreaterEqual(
                    result.technology_alignment_score,
                    Decimal("0"),
                )

                self.assertLessEqual(
                    result.technology_alignment_score,
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
                    1: ADVANCED,
                    2: ADVANCED,
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


class TechnologyCandidate2RankingTests(
    SimpleTestCase
):
    """
    Deterministic ranking guarantees for Technology Candidate T2.
    """

    def test_higher_alignment_ranks_first(
        self,
    ):
        stronger = (
            TechnologyCandidate2Result(
                career_id=1,
                career_name="Stronger Career",
                score_status=(
                    ScoreStatus.SCORED
                ),
                technology_alignment_score=(
                    Decimal("80.00")
                ),
                alignment_ratio=(
                    Decimal("0.8")
                ),
                matched_signal=(
                    Decimal("80")
                ),
                student_signal=(
                    Decimal("100")
                ),
            )
        )

        weaker = (
            TechnologyCandidate2Result(
                career_id=2,
                career_name="Weaker Career",
                score_status=(
                    ScoreStatus.SCORED
                ),
                technology_alignment_score=(
                    Decimal("40.00")
                ),
                alignment_ratio=(
                    Decimal("0.4")
                ),
                matched_signal=(
                    Decimal("40")
                ),
                student_signal=(
                    Decimal("100")
                ),
            )
        )

        ranked = (
            rank_technology_candidate_2_results(
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

    def test_identical_alignment_uses_name_tiebreak(
        self,
    ):
        alpha = (
            TechnologyCandidate2Result(
                career_id=10,
                career_name="Alpha Career",
                score_status=(
                    ScoreStatus.SCORED
                ),
                technology_alignment_score=(
                    Decimal("50.00")
                ),
                alignment_ratio=(
                    Decimal("0.5")
                ),
                matched_signal=(
                    Decimal("50")
                ),
                student_signal=(
                    Decimal("100")
                ),
            )
        )

        beta = (
            TechnologyCandidate2Result(
                career_id=20,
                career_name="Beta Career",
                score_status=(
                    ScoreStatus.SCORED
                ),
                technology_alignment_score=(
                    Decimal("50.00")
                ),
                alignment_ratio=(
                    Decimal("0.5")
                ),
                matched_signal=(
                    Decimal("50")
                ),
                student_signal=(
                    Decimal("100")
                ),
            )
        )

        ranked = (
            rank_technology_candidate_2_results(
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
            TechnologyCandidate2Result(
                career_id=1,
                career_name="Scored Career",
                score_status=(
                    ScoreStatus.SCORED
                ),
                technology_alignment_score=(
                    Decimal("50.00")
                ),
                alignment_ratio=(
                    Decimal("0.5")
                ),
                matched_signal=(
                    Decimal("50")
                ),
                student_signal=(
                    Decimal("100")
                ),
            )
        )

        insufficient = (
            TechnologyCandidate2Result(
                career_id=2,
                career_name="No Evidence Career",
                score_status=(
                    ScoreStatus.INSUFFICIENT_EVIDENCE
                ),
            )
        )

        ranked = (
            rank_technology_candidate_2_results(
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

        self.assertIsNone(
            ranked[1].rank
        )
