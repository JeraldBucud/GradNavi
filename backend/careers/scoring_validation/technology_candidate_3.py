"""
Technology Candidate 3 for GradNavi Career Fit validation.

Candidate T3 balances two different technology signals:

1. Student Alignment
   How strongly the Student's recognised technology profile
   supports the Career.

   This reuses Candidate T2's IDF-weighted Student signal.

2. Demand Coverage
   How much of the Career's source-native O*NET technology demand
   the Student covers, weighted by O*NET job-posting percentage
   and Student proficiency.

The final Technology Fit uses the harmonic mean of both signals.

Student Alignment:

    matched_student_signal
    ----------------------
    total_student_signal

Demand Coverage:

    sum(
        demand_percentage(t)
        * student_proficiency_ratio(t)
    )
    ----------------------------------
    sum(
        demand_percentage(t)
    )

Technology Fit:

    2 * alignment * coverage
    ------------------------
      alignment + coverage

This means a high score requires both:

- the Student's technologies to support the Career;
- meaningful coverage of the Career's O*NET demand profile.

Missing Career technologies contribute zero to Demand Coverage.

O*NET demand percentages stay on their source-native 0-100 scale.

Important status behaviour:

    Empty Student profile
        -> INSUFFICIENT_PROFILE

    Student has no technology represented in the global
    In-Demand evidence
        -> INSUFFICIENT_PROFILE

    Career has no In-Demand percentage evidence
        -> INSUFFICIENT_EVIDENCE

    Career has evidence but the Student matches none
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
from careers.scoring_validation.technology_candidate_1 import (
    TechnologyRequirement,
    load_in_demand_technologies_by_career,
)
from careers.scoring_validation.technology_candidate_2 import (
    TechnologyIdfWeight,
    build_technology_idf_weights,
    calculate_student_technology_signal,
)


ONET_SOURCE_NAME = "O*NET Database"

ONET_SOFTWARE_SOURCE_DOMAIN = (
    "onet_software_skills"
)

SCORE_MINIMUM = Decimal("0")
SCORE_MAXIMUM = Decimal("100")
SCORE_QUANTUM = Decimal("0.01")
ONE = Decimal("1")


@dataclass(frozen=True)
class TechnologyDemandRequirement:
    """
    One O*NET In-Demand technology with posting percentage.
    """

    career_skill_id: int

    skill_id: int
    skill_name: str

    demand_percentage: Decimal


@dataclass(frozen=True)
class TechnologyCandidate3Result:
    """
    One Technology Candidate T3 Career result.
    """

    career_id: int
    career_name: str

    score_status: ScoreStatus

    technology_fit_score: Decimal | None = None
    rank: int | None = None

    technology_fit_ratio: Decimal | None = None

    student_alignment_ratio: Decimal | None = None

    demand_coverage_ratio: Decimal | None = None

    matched_student_signal: Decimal = Decimal("0")
    student_signal: Decimal = Decimal("0")

    matched_demand_signal: Decimal = Decimal("0")
    total_demand_signal: Decimal = Decimal("0")

    matched_technology_count: int = 0
    missing_technology_count: int = 0
    career_requirement_count: int = 0

    matched_technologies: tuple[str, ...] = ()
    missing_technologies: tuple[str, ...] = ()


def load_demand_weighted_technologies_by_career(
    *,
    career_ids: Iterable[int],
) -> dict[
    int,
    tuple[
        TechnologyDemandRequirement,
        ...
    ],
]:
    """
    Load approved O*NET In-Demand technology percentages.

    Every In-Demand technology must have a percentage because
    Candidate T3 depends on the frozen O*NET API v2 snapshot.
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
        for career_id
        in selected_career_ids
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
            "-in_demand_percentage",
            "career_skill__skill__name",
            "career_skill__skill_id",
        )
    )

    requirements_by_career: dict[
        int,
        list[
            TechnologyDemandRequirement
        ],
    ] = {}

    seen_career_skill_ids: dict[
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

        percentage = (
            evidence.in_demand_percentage
        )

        if percentage is None:
            raise ValueError(
                "In-Demand O*NET technology is missing "
                "its demand percentage: "
                f"Career {career_id}, "
                f"Skill {career_skill.skill.name}"
            )

        if not (
            SCORE_MINIMUM
            <= percentage
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "O*NET demand percentage must stay "
                "within 0 to 100."
            )

        seen_ids = (
            seen_career_skill_ids
            .setdefault(
                career_id,
                set(),
            )
        )

        if career_skill.id in seen_ids:
            raise ValueError(
                "Duplicate demand-weighted technology "
                "evidence for Career "
                f"{career_id}: "
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
            TechnologyDemandRequirement(
                career_skill_id=(
                    career_skill.id
                ),
                skill_id=skill.id,
                skill_name=skill.name,
                demand_percentage=(
                    percentage
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


def calculate_technology_candidate_3_fit(
    *,
    career_id: int,
    career_name: str,
    student_proficiencies: Mapping[
        int,
        str,
    ],
    requirements: Iterable[
        TechnologyDemandRequirement
    ],
    idf_weights: Mapping[
        int,
        TechnologyIdfWeight,
    ],
    student_signal: Decimal | None = None,
) -> TechnologyCandidate3Result:
    """
    Calculate demand-weighted balanced Technology Fit.

    T3 combines:

    - IDF-weighted Student Alignment;
    - O*NET demand-weighted Career Coverage.

    The final score is their harmonic mean.
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
        return TechnologyCandidate3Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_PROFILE
            ),
        )

    if not requirement_list:
        return TechnologyCandidate3Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
        )

    if student_signal is None:
        student_signal = (
            calculate_student_technology_signal(
                student_proficiencies=(
                    student_proficiencies
                ),
                idf_weights=(
                    idf_weights
                ),
            )
        )

    if student_signal <= SCORE_MINIMUM:
        return TechnologyCandidate3Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_PROFILE
            ),
            career_requirement_count=(
                len(
                    requirement_list
                )
            ),
        )

    seen_career_skill_ids = set()

    matched_student_signal = Decimal("0")

    matched_demand_signal = Decimal("0")
    total_demand_signal = Decimal("0")

    matched_names = []
    missing_names = []

    for requirement in requirement_list:
        if (
            requirement.career_skill_id
            in seen_career_skill_ids
        ):
            raise ValueError(
                "Duplicate demand-weighted technology "
                "requirement was supplied."
            )

        seen_career_skill_ids.add(
            requirement.career_skill_id
        )

        percentage = (
            requirement.demand_percentage
        )

        if not (
            SCORE_MINIMUM
            <= percentage
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "Demand percentage must stay "
                "within 0 to 100."
            )

        total_demand_signal += (
            percentage
        )

        weight = idf_weights.get(
            requirement.skill_id
        )

        if weight is None:
            raise ValueError(
                "Technology requirement is missing "
                "its global IDF weight: "
                f"{requirement.skill_name}"
            )

        proficiency_level = (
            student_proficiencies.get(
                requirement.skill_id
            )
        )

        if proficiency_level is None:
            missing_names.append(
                requirement.skill_name
            )

            continue

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

        proficiency_ratio = (
            student_score
            / SCORE_MAXIMUM
        )

        matched_student_signal += (
            student_score
            * weight.idf_weight
        )

        matched_demand_signal += (
            percentage
            * proficiency_ratio
        )

        matched_names.append(
            requirement.skill_name
        )

    if total_demand_signal <= SCORE_MINIMUM:
        return TechnologyCandidate3Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
            student_signal=(
                student_signal
            ),
            career_requirement_count=(
                len(
                    requirement_list
                )
            ),
        )

    student_alignment_ratio = (
        matched_student_signal
        / student_signal
    )

    if student_alignment_ratio < Decimal("0"):
        student_alignment_ratio = Decimal("0")

    if student_alignment_ratio > ONE:
        student_alignment_ratio = ONE

    demand_coverage_ratio = (
        matched_demand_signal
        / total_demand_signal
    )

    if demand_coverage_ratio < Decimal("0"):
        demand_coverage_ratio = Decimal("0")

    if demand_coverage_ratio > ONE:
        demand_coverage_ratio = ONE

    if (
        student_alignment_ratio
        <= Decimal("0")
        or demand_coverage_ratio
        <= Decimal("0")
    ):
        technology_fit_ratio = Decimal("0")

    else:
        technology_fit_ratio = (
            (
                Decimal("2")
                * student_alignment_ratio
                * demand_coverage_ratio
            )
            /
            (
                student_alignment_ratio
                + demand_coverage_ratio
            )
        )

    if technology_fit_ratio < Decimal("0"):
        technology_fit_ratio = Decimal("0")

    if technology_fit_ratio > ONE:
        technology_fit_ratio = ONE

    technology_fit_score = (
        (
            technology_fit_ratio
            * SCORE_MAXIMUM
        )
        .quantize(
            SCORE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
    )

    matched_technologies = tuple(
        sorted(
            matched_names,
            key=str.casefold,
        )
    )

    missing_technologies = tuple(
        sorted(
            missing_names,
            key=str.casefold,
        )
    )

    return TechnologyCandidate3Result(
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
        student_alignment_ratio=(
            student_alignment_ratio
        ),
        demand_coverage_ratio=(
            demand_coverage_ratio
        ),
        matched_student_signal=(
            matched_student_signal
        ),
        student_signal=(
            student_signal
        ),
        matched_demand_signal=(
            matched_demand_signal
        ),
        total_demand_signal=(
            total_demand_signal
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
        career_requirement_count=(
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


def rank_technology_candidate_3_results(
    results: Iterable[
        TechnologyCandidate3Result
    ],
) -> tuple[
    TechnologyCandidate3Result,
    ...
]:
    """
    Rank Technology Candidate T3 deterministically.

    Tie breakers:

    1. Higher exact Technology Fit.
    2. Higher demand coverage.
    3. Higher Student alignment.
    4. Higher matched demand signal.
    5. Career name alphabetically.
    6. Career ID ascending.
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
            if result.technology_fit_ratio is None:
                raise ValueError(
                    "A scored Technology Candidate T3 "
                    "result must have technology_fit_ratio."
                )

            if result.demand_coverage_ratio is None:
                raise ValueError(
                    "A scored Technology Candidate T3 "
                    "result must have demand_coverage_ratio."
                )

            if result.student_alignment_ratio is None:
                raise ValueError(
                    "A scored Technology Candidate T3 "
                    "result must have student_alignment_ratio."
                )

            if result.technology_fit_score is None:
                raise ValueError(
                    "A scored Technology Candidate T3 "
                    "result must have technology_fit_score."
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
            -result.demand_coverage_ratio,
            -result.student_alignment_ratio,
            -result.matched_demand_signal,
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
        for result
        in unscored
    )

    return (
        ranked
        + unranked
    )


def score_profile_with_technology_candidate_3(
    *,
    student_proficiencies: Mapping[
        int,
        str,
    ],
) -> tuple[
    TechnologyCandidate3Result,
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

    t2_requirements_by_career = (
        load_in_demand_technologies_by_career(
            career_ids=career_ids
        )
    )

    demand_requirements_by_career = (
        load_demand_weighted_technologies_by_career(
            career_ids=career_ids
        )
    )

    idf_weights = (
        build_technology_idf_weights(
            requirements_by_career=(
                t2_requirements_by_career
            )
        )
    )

    student_signal = (
        calculate_student_technology_signal(
            student_proficiencies=(
                student_proficiencies
            ),
            idf_weights=(
                idf_weights
            ),
        )
    )

    results = []

    for career in careers:
        results.append(
            calculate_technology_candidate_3_fit(
                career_id=career.id,
                career_name=career.name,
                student_proficiencies=(
                    student_proficiencies
                ),
                requirements=(
                    demand_requirements_by_career.get(
                        career.id,
                        (),
                    )
                ),
                idf_weights=(
                    idf_weights
                ),
                student_signal=(
                    student_signal
                ),
            )
        )

    return (
        rank_technology_candidate_3_results(
            results
        )
    )
