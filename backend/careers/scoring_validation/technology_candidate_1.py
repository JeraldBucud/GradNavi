"""
Technology Candidate 1 for GradNavi Career Fit validation.

Candidate T1 evaluates a Student's proficiency across the
occupation-specific technologies marked In Demand by O*NET.

Only approved, active O*NET Software Skills evidence with:

    in_demand = True

is numerically scored.

Hot Technology is retained as explanatory source evidence but is
not given an invented numerical weight in Candidate T1.

Formula:

    contribution_i =
        student_proficiency_i / 100

    technology_fit_ratio =
        sum(
            contribution_i
            for each In-Demand technology
        )
        /
        number_of_in_demand_technologies

    technology_fit =
        technology_fit_ratio * 100

Missing technologies contribute zero.

Important status behaviour:

    Empty Student profile
        -> INSUFFICIENT_PROFILE

    Career with no In-Demand technology evidence
        -> INSUFFICIENT_EVIDENCE

    Career has In-Demand technologies but Student matches none
        -> SCORED with 0.00

This module is experimental validation code only.
Production WBS 5.3 scoring is not modified.
"""

from dataclasses import dataclass, replace
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Mapping

from careers.models import (
    Career,
    CareerSkillEvidence,
    ReferenceDataset,
    ReviewStatus,
)
from careers.services.recommendation_scoring import (
    ScoreStatus,
)
from careers.services.readiness_scoring import (
    map_student_proficiency,
)


ONET_SOURCE_NAME = "O*NET Database"

ONET_SOFTWARE_SOURCE_DOMAIN = (
    "onet_software_skills"
)

SCORE_MINIMUM = Decimal("0")
SCORE_MAXIMUM = Decimal("100")
SCORE_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class TechnologyRequirement:
    """
    One occupation-specific In-Demand technology.
    """

    career_skill_id: int
    skill_id: int
    skill_name: str

    hot_technology: bool


@dataclass(frozen=True)
class TechnologyCandidate1Result:
    """
    One Technology Candidate T1 Career result.
    """

    career_id: int
    career_name: str

    score_status: ScoreStatus

    technology_fit_score: Decimal | None = None
    rank: int | None = None

    technology_fit_ratio: Decimal | None = None

    matched_technology_count: int = 0
    missing_technology_count: int = 0
    technology_requirement_count: int = 0

    matched_technologies: tuple[str, ...] = ()
    missing_technologies: tuple[str, ...] = ()


def load_in_demand_technologies_by_career(
    *,
    career_ids: Iterable[int],
) -> dict[
    int,
    tuple[TechnologyRequirement, ...],
]:
    """
    Load approved O*NET In-Demand technology evidence.

    Only source-native occupation-specific In Demand=True
    relationships are numerically eligible for Candidate T1.
    """

    selected_career_ids = tuple(
        dict.fromkeys(
            career_ids
        )
    )

    if not selected_career_ids:
        return {}

    if any(
        career_id <= 0
        for career_id in selected_career_ids
    ):
        raise ValueError(
            "career_ids must contain only "
            "positive integers."
        )

    evidence_rows = (
        CareerSkillEvidence.objects
        .select_related(
            "career_skill__skill",
        )
        .filter(
            career_skill__career_id__in=(
                selected_career_ids
            ),
            career_skill__review_status=(
                ReviewStatus.APPROVED
            ),
            dataset__status=(
                ReferenceDataset.Status.ACTIVE
            ),
            dataset__source__name=(
                ONET_SOURCE_NAME
            ),
            source_domain=(
                ONET_SOFTWARE_SOURCE_DOMAIN
            ),
            in_demand=True,
            not_relevant=False,
        )
        .exclude(
            recommend_suppress=True
        )
        .order_by(
            "career_skill__career_id",
            "career_skill__skill__name",
            "career_skill__skill_id",
        )
    )

    requirements_by_career: dict[
        int,
        list[TechnologyRequirement],
    ] = {}

    seen_career_skill_ids_by_career: dict[
        int,
        set[int],
    ] = {}

    for evidence in evidence_rows:
        career_skill = (
            evidence.career_skill
        )

        career_id = (
            career_skill.career_id
        )

        seen_ids = (
            seen_career_skill_ids_by_career
            .setdefault(
                career_id,
                set(),
            )
        )

        if career_skill.id in seen_ids:
            raise ValueError(
                "Duplicate In-Demand technology "
                "evidence for Career "
                f"{career_id}: "
                f"CareerSkill "
                f"{career_skill.id}"
            )

        seen_ids.add(
            career_skill.id
        )

        skill = career_skill.skill

        requirements_by_career.setdefault(
            career_id,
            [],
        ).append(
            TechnologyRequirement(
                career_skill_id=(
                    career_skill.id
                ),
                skill_id=skill.id,
                skill_name=skill.name,
                hot_technology=bool(
                    evidence.hot_technology
                ),
            )
        )

    return {
        career_id: tuple(
            requirements
        )
        for career_id, requirements
        in requirements_by_career.items()
    }


def calculate_technology_candidate_1_fit(
    *,
    career_id: int,
    career_name: str,
    student_proficiencies: Mapping[
        int,
        str,
    ],
    requirements: Iterable[
        TechnologyRequirement
    ],
) -> TechnologyCandidate1Result:
    """
    Calculate Candidate T1 Technology Fit.

    The calculation is intentionally simple:

        sum(Student proficiency scores)
        --------------------------------
        100 * number of In-Demand technologies

    Missing In-Demand technologies contribute zero.
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
        return TechnologyCandidate1Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_PROFILE
            ),
        )

    if not requirement_list:
        return TechnologyCandidate1Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
        )

    seen_career_skill_ids = set()

    proficiency_sum = Decimal("0")

    matched_technology_names = []
    missing_technology_names = []

    for requirement in requirement_list:
        if (
            requirement.career_skill_id
            in seen_career_skill_ids
        ):
            raise ValueError(
                "Duplicate In-Demand technology "
                "requirement was supplied."
            )

        seen_career_skill_ids.add(
            requirement.career_skill_id
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

        if not (
            SCORE_MINIMUM
            <= student_score
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "Mapped Student proficiency must "
                "stay within 0 to 100."
            )

        if proficiency_level is None:
            missing_technology_names.append(
                requirement.skill_name
            )
        else:
            matched_technology_names.append(
                requirement.skill_name
            )

        proficiency_sum += (
            student_score
        )

    denominator = (
        SCORE_MAXIMUM
        * Decimal(
            len(requirement_list)
        )
    )

    if denominator <= SCORE_MINIMUM:
        return TechnologyCandidate1Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
        )

    technology_fit_ratio = (
        proficiency_sum
        / denominator
    )

    if technology_fit_ratio < Decimal("0"):
        technology_fit_ratio = Decimal("0")

    if technology_fit_ratio > Decimal("1"):
        technology_fit_ratio = Decimal("1")

    unrounded_score = (
        technology_fit_ratio
        * SCORE_MAXIMUM
    )

    technology_fit_score = (
        unrounded_score.quantize(
            SCORE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
    )

    matched_technologies = tuple(
        sorted(
            matched_technology_names,
            key=str.casefold,
        )
    )

    missing_technologies = tuple(
        sorted(
            missing_technology_names,
            key=str.casefold,
        )
    )

    return TechnologyCandidate1Result(
        career_id=career_id,
        career_name=career_name,
        score_status=(
            ScoreStatus.SCORED
        ),
        technology_fit_score=(
            technology_fit_score
        ),
        technology_fit_ratio=(
            technology_fit_ratio
        ),
        matched_technology_count=(
            len(
                matched_technologies
            )
        ),
        missing_technology_count=(
            len(
                missing_technologies
            )
        ),
        technology_requirement_count=(
            len(
                requirement_list
            )
        ),
        matched_technologies=(
            matched_technologies
        ),
        missing_technologies=(
            missing_technologies
        ),
    )


def rank_technology_candidate_1_results(
    results: Iterable[
        TechnologyCandidate1Result
    ],
) -> tuple[
    TechnologyCandidate1Result,
    ...
]:
    """
    Rank Candidate T1 deterministically.

    Higher exact Technology Fit ranks first.

    Tie breakers:

    1. Higher exact technology_fit_ratio.
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
                result.technology_fit_ratio
                is None
            ):
                raise ValueError(
                    "A scored Technology Candidate "
                    "T1 result must have "
                    "technology_fit_ratio."
                )

            if (
                result.technology_fit_score
                is None
            ):
                raise ValueError(
                    "A scored Technology Candidate "
                    "T1 result must have a "
                    "Technology Fit score."
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
            -result.technology_fit_ratio,
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


def score_profile_with_technology_candidate_1(
    *,
    student_proficiencies: Mapping[
        int,
        str,
    ],
) -> tuple[
    TechnologyCandidate1Result,
    ...
]:
    """
    Score one in-memory Student profile against all active Careers.
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
        load_in_demand_technologies_by_career(
            career_ids=career_ids
        )
    )

    results = []

    for career in careers:
        results.append(
            calculate_technology_candidate_1_fit(
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

    return (
        rank_technology_candidate_1_results(
            results
        )
    )