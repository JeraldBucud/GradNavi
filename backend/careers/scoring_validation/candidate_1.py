"""
Candidate 1 for GradNavi Career Fit scoring.

Candidate 1 evaluates whether proficiency-aware O*NET requirement
attainment improves recommendation ranking over WBS 5.3 Version 1.

Formula for one competency:

    student_score =
        Foundational -> 25
        Developing   -> 50
        Proficient   -> 75
        Advanced     -> 100
        Missing      -> 0

    attainment =
        min(
            student_score / required_level,
            1
        )

    weighted_contribution =
        importance * attainment

Career competency fit:

    sum(weighted_contribution)
    -------------------------- * 100
        sum(importance)

This experiment uses production source-backed O*NET Importance and
Level values, and the existing GradNavi proficiency scale.

It does NOT modify production WBS 5.3.
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
    ONET_SOURCE_NAME,
    ScoreStatus,
)
from careers.services.readiness_scoring import (
    CareerReadinessRequirement,
    ONET_NUMERICAL_SOURCE_DOMAINS,
    READINESS_CONCEPT_TYPES,
    map_student_proficiency,
)


SCORE_MINIMUM = Decimal("0")
SCORE_MAXIMUM = Decimal("100")
SCORE_QUANTUM = Decimal("0.01")
ATTAINMENT_MAXIMUM = Decimal("1")


@dataclass(frozen=True)
class Candidate1Result:
    """
    One Candidate 1 Career Fit result.
    """

    career_id: int
    career_name: str

    score_status: ScoreStatus

    career_fit_score: Decimal | None = None
    rank: int | None = None

    total_importance_weight: Decimal = Decimal("0")
    weighted_attainment: Decimal = Decimal("0")

    matched_requirement_count: int = 0
    missing_requirement_count: int = 0

    requirement_count: int = 0


def load_requirements_by_career(
    *,
    career_ids: Iterable[int],
) -> dict[
    int,
    tuple[
        CareerReadinessRequirement,
        ...
    ],
]:
    """
    Load source-backed O*NET Importance + Level requirements.

    Eligibility deliberately mirrors WBS 5.5 readiness evidence:

    - active ReferenceDataset;
    - approved CareerSkill;
    - O*NET source;
    - approved numerical domain;
    - Importance present;
    - Level present;
    - Skill or Knowledge concept;
    - not marked irrelevant;
    - not suppressed.
    """

    unique_career_ids = tuple(
        dict.fromkeys(
            career_ids
        )
    )

    if not unique_career_ids:
        return {}

    grouped = {
        career_id: []
        for career_id
        in unique_career_ids
    }

    rows = (
        CareerSkillEvidence.objects
        .select_related(
            "career_skill__skill",
        )
        .filter(
            career_skill__career_id__in=(
                unique_career_ids
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
            source_domain__in=(
                ONET_NUMERICAL_SOURCE_DOMAINS
            ),
            normalized_importance__isnull=False,
            normalized_level__isnull=False,
            career_skill__skill__concept_type__in=(
                READINESS_CONCEPT_TYPES
            ),
            not_relevant=False,
        )
        .exclude(
            recommend_suppress=True
        )
        .order_by(
            "career_skill__career_id",
            "career_skill_id",
            "id",
        )
    )

    for evidence in rows:
        career_id = (
            evidence
            .career_skill
            .career_id
        )

        skill = (
            evidence
            .career_skill
            .skill
        )

        grouped[
            career_id
        ].append(
            CareerReadinessRequirement(
                career_skill_id=(
                    evidence.career_skill_id
                ),
                skill_id=skill.id,
                skill_name=skill.name,
                concept_type=(
                    skill.concept_type
                ),
                source_domain=(
                    evidence.source_domain
                ),
                importance=(
                    evidence.normalized_importance
                ),
                required_level=(
                    evidence.normalized_level
                ),
            )
        )

    return {
        career_id: tuple(
            requirements
        )
        for (
            career_id,
            requirements,
        )
        in grouped.items()
    }


def calculate_candidate_1_fit(
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
) -> Candidate1Result:
    """
    Calculate proficiency-aware competency Career Fit.

    This is a pure calculation and performs no database writes.
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
        return Candidate1Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_PROFILE
            ),
        )

    if not requirement_list:
        return Candidate1Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
        )

    seen_career_skill_ids = set()

    total_importance_weight = (
        Decimal("0")
    )

    weighted_attainment = (
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

        if not (
            SCORE_MINIMUM
            <= requirement.importance
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "Importance must stay "
                "within 0 to 100."
            )

        if not (
            SCORE_MINIMUM
            < requirement.required_level
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "Required Level must be greater "
                "than 0 and at most 100."
            )

        student_proficiency_level = (
            student_proficiencies.get(
                requirement.skill_id
            )
        )

        student_score = (
            map_student_proficiency(
                student_proficiency_level
            )
        )

        if student_proficiency_level is None:
            missing_requirement_count += 1
        else:
            matched_requirement_count += 1

        raw_attainment = (
            student_score
            / requirement.required_level
        )

        attainment = min(
            raw_attainment,
            ATTAINMENT_MAXIMUM,
        )

        weighted_contribution = (
            requirement.importance
            * attainment
        )

        total_importance_weight += (
            requirement.importance
        )

        weighted_attainment += (
            weighted_contribution
        )

    if (
        total_importance_weight
        <= SCORE_MINIMUM
    ):
        return Candidate1Result(
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

    unrounded_score = (
        weighted_attainment
        / total_importance_weight
        * SCORE_MAXIMUM
    )

    career_fit_score = (
        unrounded_score.quantize(
            SCORE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
    )

    if not (
        SCORE_MINIMUM
        <= career_fit_score
        <= SCORE_MAXIMUM
    ):
        raise ValueError(
            "Candidate 1 Career Fit must "
            "stay within 0 to 100."
        )

    return Candidate1Result(
        career_id=career_id,
        career_name=career_name,
        score_status=(
            ScoreStatus.SCORED
        ),
        career_fit_score=(
            career_fit_score
        ),
        total_importance_weight=(
            total_importance_weight
        ),
        weighted_attainment=(
            weighted_attainment
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


def rank_candidate_1_results(
    results: Iterable[
        Candidate1Result
    ],
) -> tuple[
    Candidate1Result,
    ...
]:
    """
    Rank Candidate 1 results deterministically.

    Ranking uses the exact unrounded weighted-attainment ratio.

    Tie breakers:

    1. Higher attainment ratio.
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
                result.total_importance_weight
                <= SCORE_MINIMUM
            ):
                raise ValueError(
                    "A scored Candidate 1 result "
                    "must have positive total weight."
                )

            if (
                result.career_fit_score
                is None
            ):
                raise ValueError(
                    "A scored Candidate 1 result "
                    "must have a score."
                )

            scored.append(
                result
            )

        else:
            unscored.append(
                result
            )

    def exact_ratio(
        result: Candidate1Result,
    ) -> Decimal:
        return (
            result.weighted_attainment
            / result.total_importance_weight
        )

    scored.sort(
        key=lambda result: (
            -exact_ratio(
                result
            ),
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


def score_profile_with_candidate_1(
    *,
    student_proficiencies: Mapping[
        int,
        str,
    ],
) -> tuple[
    Candidate1Result,
    ...
]:
    """
    Score an in-memory Student proficiency profile against every
    active Career.

    This is the Candidate 1 equivalent of production recommendation
    generation, but it performs no StudentProfile database writes.
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
            calculate_candidate_1_fit(
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

    return rank_candidate_1_results(
        results
    )