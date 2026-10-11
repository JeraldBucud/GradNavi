"""
Candidate 2 for GradNavi Career Fit scoring.

Candidate 2 evaluates proficiency-to-requirement deficit using a
normalized weighted Euclidean distance.

Research basis:

- Student proficiency above a Career requirement is capped at the
  requirement and therefore creates no additional reward.
- Deficits are measured as distance from Career requirements.
- O*NET Importance weights larger deficiencies in more important
  competencies more strongly.
- Distance is normalized against the maximum possible deficit for
  that Career so Careers with different requirement counts remain
  comparable.

Formula:

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

    normalized_deficit =
        weighted_distance / maximum_distance

    career_fit =
        (1 - normalized_deficit) * 100

This module is experimental validation code only.
Production WBS 5.3 is not modified.
"""

from dataclasses import dataclass, replace
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Mapping

from careers.models import Career
from careers.services.recommendation_scoring import (
    ScoreStatus,
)
from careers.services.readiness_scoring import (
    CareerReadinessRequirement,
    map_student_proficiency,
)

from careers.scoring_validation.candidate_1 import (
    load_requirements_by_career,
)


SCORE_MINIMUM = Decimal("0")
SCORE_MAXIMUM = Decimal("100")
SCORE_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class Candidate2Result:
    """
    One Candidate 2 Career Fit result.
    """

    career_id: int
    career_name: str

    score_status: ScoreStatus

    career_fit_score: Decimal | None = None
    rank: int | None = None

    weighted_squared_deficit: Decimal = Decimal("0")
    maximum_weighted_squared_deficit: Decimal = Decimal("0")

    normalized_deficit: Decimal | None = None

    matched_requirement_count: int = 0
    missing_requirement_count: int = 0
    requirement_count: int = 0


def calculate_candidate_2_fit(
    *,
    career_id: int,
    career_name: str,
    student_proficiencies: Mapping[
        int,
        str,
    ],
    requirements: Iterable[
        CareerReadinessRequirement
    ],
) -> Candidate2Result:
    """
    Calculate normalized weighted competency-deficit Career Fit.

    This is a pure calculation.
    """

    if career_id <= 0:
        raise ValueError(
            "career_id must be greater than zero."
        )

    if not career_name.strip():
        raise ValueError(
            "career_name must not be blank."
        )

    requirement_list = tuple(
        requirements
    )

    if not student_proficiencies:
        return Candidate2Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_PROFILE
            ),
        )

    if not requirement_list:
        return Candidate2Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
        )

    seen_career_skill_ids = set()

    weighted_squared_deficit = (
        Decimal("0")
    )

    maximum_weighted_squared_deficit = (
        Decimal("0")
    )

    matched_requirement_count = 0
    missing_requirement_count = 0

    for requirement in requirement_list:
        if (
            requirement.career_skill_id
            in seen_career_skill_ids
        ):
            raise ValueError(
                "Duplicate CareerSkill requirement "
                "was supplied."
            )

        seen_career_skill_ids.add(
            requirement.career_skill_id
        )

        importance = (
            requirement.importance
        )

        required_level = (
            requirement.required_level
        )

        if not (
            SCORE_MINIMUM
            <= importance
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "Importance must stay "
                "within 0 to 100."
            )

        if not (
            SCORE_MINIMUM
            < required_level
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "Required Level must be greater "
                "than 0 and at most 100."
            )

        proficiency_level = (
            student_proficiencies.get(
                requirement.skill_id
            )
        )

        student_score = (
            map_student_proficiency(
                proficiency_level
            )
        )

        if proficiency_level is None:
            missing_requirement_count += 1
        else:
            matched_requirement_count += 1

        deficit = max(
            required_level
            - student_score,
            SCORE_MINIMUM,
        )

        weighted_squared_deficit += (
            importance
            * deficit
            * deficit
        )

        maximum_weighted_squared_deficit += (
            importance
            * required_level
            * required_level
        )

    if (
        maximum_weighted_squared_deficit
        <= SCORE_MINIMUM
    ):
        return Candidate2Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
            matched_requirement_count=(
                matched_requirement_count
            ),
            missing_requirement_count=(
                missing_requirement_count
            ),
            requirement_count=(
                len(requirement_list)
            ),
        )

    weighted_distance = (
        weighted_squared_deficit.sqrt()
    )

    maximum_distance = (
        maximum_weighted_squared_deficit.sqrt()
    )

    normalized_deficit = (
        weighted_distance
        / maximum_distance
    )

    if normalized_deficit < SCORE_MINIMUM:
        normalized_deficit = (
            SCORE_MINIMUM
        )

    if normalized_deficit > Decimal("1"):
        normalized_deficit = Decimal("1")

    unrounded_score = (
        (
            Decimal("1")
            - normalized_deficit
        )
        * SCORE_MAXIMUM
    )

    career_fit_score = (
        unrounded_score.quantize(
            SCORE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
    )

    return Candidate2Result(
        career_id=career_id,
        career_name=career_name,
        score_status=(
            ScoreStatus.SCORED
        ),
        career_fit_score=(
            career_fit_score
        ),
        weighted_squared_deficit=(
            weighted_squared_deficit
        ),
        maximum_weighted_squared_deficit=(
            maximum_weighted_squared_deficit
        ),
        normalized_deficit=(
            normalized_deficit
        ),
        matched_requirement_count=(
            matched_requirement_count
        ),
        missing_requirement_count=(
            missing_requirement_count
        ),
        requirement_count=(
            len(requirement_list)
        ),
    )


def rank_candidate_2_results(
    results: Iterable[
        Candidate2Result
    ],
) -> tuple[
    Candidate2Result,
    ...
]:
    """
    Rank Candidate 2 deterministically.

    Lower normalized deficit means stronger Career Fit.

    Tie breakers:

    1. Lower exact normalized deficit.
    2. Career name alphabetically.
    3. Career ID ascending.
    """

    result_list = tuple(
        results
    )

    scored = []
    unscored = []

    for result in result_list:
        if (
            result.score_status
            == ScoreStatus.SCORED
        ):
            if (
                result.normalized_deficit
                is None
            ):
                raise ValueError(
                    "A scored Candidate 2 result "
                    "must have normalized_deficit."
                )

            if (
                result.career_fit_score
                is None
            ):
                raise ValueError(
                    "A scored Candidate 2 result "
                    "must have a Career Fit score."
                )

            scored.append(
                result
            )

        else:
            unscored.append(
                result
            )

    scored.sort(
        key=lambda result: (
            result.normalized_deficit,
            result.career_name.casefold(),
            result.career_id,
        )
    )

    ranked = tuple(
        replace(
            result,
            rank=index,
        )
        for index, result
        in enumerate(
            scored,
            start=1,
        )
    )

    unscored.sort(
        key=lambda result: (
            result.career_name.casefold(),
            result.career_id,
        )
    )

    unranked = tuple(
        replace(
            result,
            rank=None,
        )
        for result in unscored
    )

    return (
        ranked
        + unranked
    )


def score_profile_with_candidate_2(
    *,
    student_proficiencies: Mapping[
        int,
        str,
    ],
) -> tuple[
    Candidate2Result,
    ...
]:
    """
    Score an in-memory Student profile against all active Careers.
    """

    careers = tuple(
        Career.objects
        .filter(
            active=True
        )
        .order_by(
            "name",
            "id",
        )
        .only(
            "id",
            "name",
        )
    )

    if not careers:
        return ()

    career_ids = tuple(
        career.id
        for career in careers
    )

    requirements_by_career = (
        load_requirements_by_career(
            career_ids=career_ids
        )
    )

    results = []

    for career in careers:
        results.append(
            calculate_candidate_2_fit(
                career_id=career.id,
                career_name=career.name,
                student_proficiencies=(
                    student_proficiencies
                ),
                requirements=(
                    requirements_by_career.get(
                        career.id,
                        (),
                    )
                ),
            )
        )

    return rank_candidate_2_results(
        results
    )