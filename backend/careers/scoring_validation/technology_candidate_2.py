"""
Technology Candidate 2 for GradNavi Career Fit validation.

Candidate T2 measures how strongly the Student's existing
technology profile aligns with each Career's occupation-specific
O*NET In-Demand technologies.

Unlike Technology Candidate T1, T2 is Student-centred.

T1 asks:

    How much of the Career's full technology catalogue
    does the Student cover?

T2 asks:

    How much of the Student's recognised technology signal
    supports this Career?

Technologies are weighted using an IDF-style discriminative weight.

For technology t:

    idf(t) =
        ln(
            (N + 1)
            /
            (df(t) + 1)
        )
        + 1

Where:

    N
        Number of Careers with usable In-Demand technology evidence.

    df(t)
        Number of supported Careers where technology t is In Demand.

A technology appearing in many Careers receives less
discriminative weight.

A technology appearing in fewer Careers receives more
discriminative weight.

Student proficiency is also included:

    Foundational = 25
    Developing   = 50
    Proficient   = 75
    Advanced     = 100

Student technology signal:

    student_signal =
        sum(
            proficiency(t)
            * idf(t)
        )

for Student technologies appearing somewhere in the approved
O*NET In-Demand technology evidence.

Career matched signal:

    matched_signal(c) =
        sum(
            proficiency(t)
            * idf(t)
        )

for Student technologies that are also In Demand for Career c.

Technology Alignment:

    alignment_ratio =
        matched_signal(c)
        /
        student_signal

    technology_alignment =
        alignment_ratio * 100

Important status behaviour:

    Empty Student profile
        -> INSUFFICIENT_PROFILE

    Student has no technologies represented in the global
    In-Demand evidence
        -> INSUFFICIENT_PROFILE

    Career has no In-Demand technology evidence
        -> INSUFFICIENT_EVIDENCE

    Career has evidence but none of the Student's recognised
    technologies match
        -> SCORED with 0.00

This module is experimental validation code only.
Production WBS 5.3 scoring is not modified.
"""

from dataclasses import dataclass, replace
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Mapping

from careers.models import Career
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


SCORE_MINIMUM = Decimal("0")
SCORE_MAXIMUM = Decimal("100")
SCORE_QUANTUM = Decimal("0.01")
ONE = Decimal("1")


@dataclass(frozen=True)
class TechnologyIdfWeight:
    """
    Global discriminative weight for one In-Demand technology.
    """

    skill_id: int
    skill_name: str

    document_frequency: int
    supported_career_count: int

    idf_weight: Decimal


@dataclass(frozen=True)
class TechnologyCandidate2Result:
    """
    One Technology Candidate T2 Career result.
    """

    career_id: int
    career_name: str

    score_status: ScoreStatus

    technology_alignment_score: Decimal | None = None
    rank: int | None = None

    alignment_ratio: Decimal | None = None

    matched_signal: Decimal = Decimal("0")
    student_signal: Decimal = Decimal("0")

    matched_technology_count: int = 0
    missing_technology_count: int = 0
    career_requirement_count: int = 0

    matched_technologies: tuple[str, ...] = ()
    missing_technologies: tuple[str, ...] = ()


def build_technology_idf_weights(
    *,
    requirements_by_career: Mapping[
        int,
        Iterable[
            TechnologyRequirement
        ],
    ],
) -> dict[
    int,
    TechnologyIdfWeight,
]:
    """
    Calculate global IDF-style technology weights.

    Only Careers with at least one In-Demand technology contribute
    to N.

    df(t) counts how many supported Careers contain technology t.
    """

    supported_careers = {
        career_id: tuple(
            requirements
        )
        for career_id, requirements
        in requirements_by_career.items()
        if tuple(requirements)
    }

    supported_career_count = len(
        supported_careers
    )

    if supported_career_count == 0:
        return {}

    career_ids_by_skill: dict[
        int,
        set[int],
    ] = {}

    skill_names: dict[
        int,
        str,
    ] = {}

    for (
        career_id,
        requirements,
    ) in supported_careers.items():
        seen_skill_ids = set()

        for requirement in requirements:
            if (
                requirement.skill_id
                in seen_skill_ids
            ):
                raise ValueError(
                    "Duplicate In-Demand technology "
                    "within Career "
                    f"{career_id}: "
                    f"{requirement.skill_id}"
                )

            seen_skill_ids.add(
                requirement.skill_id
            )

            existing_name = (
                skill_names.get(
                    requirement.skill_id
                )
            )

            if (
                existing_name is not None
                and existing_name
                != requirement.skill_name
            ):
                raise ValueError(
                    "A canonical Skill ID cannot have "
                    "multiple names."
                )

            skill_names[
                requirement.skill_id
            ] = requirement.skill_name

            career_ids_by_skill.setdefault(
                requirement.skill_id,
                set(),
            ).add(
                career_id
            )

    weights = {}

    for (
        skill_id,
        career_ids,
    ) in career_ids_by_skill.items():
        document_frequency = len(
            career_ids
        )

        if (
            document_frequency <= 0
            or document_frequency
            > supported_career_count
        ):
            raise ValueError(
                "Technology document frequency "
                "is outside the valid range."
            )

        numerator = Decimal(
            supported_career_count
            + 1
        )

        denominator = Decimal(
            document_frequency
            + 1
        )

        idf_weight = (
            (
                numerator
                / denominator
            ).ln()
            + ONE
        )

        weights[
            skill_id
        ] = TechnologyIdfWeight(
            skill_id=skill_id,
            skill_name=(
                skill_names[
                    skill_id
                ]
            ),
            document_frequency=(
                document_frequency
            ),
            supported_career_count=(
                supported_career_count
            ),
            idf_weight=(
                idf_weight
            ),
        )

    return weights


def calculate_student_technology_signal(
    *,
    student_proficiencies: Mapping[
        int,
        str,
    ],
    idf_weights: Mapping[
        int,
        TechnologyIdfWeight,
    ],
) -> Decimal:
    """
    Calculate the Student's total globally recognised technology signal.

    Student Skills not represented in any approved In-Demand
    technology evidence do not contribute to this component.
    """

    signal = Decimal("0")

    for (
        skill_id,
        proficiency_level,
    ) in student_proficiencies.items():
        weight = idf_weights.get(
            skill_id
        )

        if weight is None:
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

        signal += (
            student_score
            * weight.idf_weight
        )

    return signal


def calculate_technology_candidate_2_fit(
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
    idf_weights: Mapping[
        int,
        TechnologyIdfWeight,
    ],
    student_signal: Decimal | None = None,
) -> TechnologyCandidate2Result:
    """
    Calculate Student-centred Technology Alignment for one Career.
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
        return TechnologyCandidate2Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_PROFILE
            ),
        )

    if not requirement_list:
        return TechnologyCandidate2Result(
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
        return TechnologyCandidate2Result(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_PROFILE
            ),
            career_requirement_count=(
                len(requirement_list)
            ),
        )

    seen_career_skill_ids = set()

    matched_signal = Decimal("0")

    matched_names = []
    missing_names = []

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

        matched_signal += (
            student_score
            * weight.idf_weight
        )

        matched_names.append(
            requirement.skill_name
        )

    alignment_ratio = (
        matched_signal
        / student_signal
    )

    if alignment_ratio < Decimal("0"):
        alignment_ratio = Decimal("0")

    if alignment_ratio > Decimal("1"):
        alignment_ratio = Decimal("1")

    unrounded_score = (
        alignment_ratio
        * SCORE_MAXIMUM
    )

    technology_alignment_score = (
        unrounded_score.quantize(
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

    return TechnologyCandidate2Result(
        career_id=career_id,
        career_name=career_name,
        score_status=(
            ScoreStatus.SCORED
        ),
        technology_alignment_score=(
            technology_alignment_score
        ),
        alignment_ratio=(
            alignment_ratio
        ),
        matched_signal=(
            matched_signal
        ),
        student_signal=(
            student_signal
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


def rank_technology_candidate_2_results(
    results: Iterable[
        TechnologyCandidate2Result
    ],
) -> tuple[
    TechnologyCandidate2Result,
    ...
]:
    """
    Rank Technology Candidate T2 deterministically.

    Higher exact alignment ratio ranks first.

    Tie breakers:

    1. Higher exact alignment ratio.
    2. Higher exact matched signal.
    3. Career name alphabetically.
    4. Career ID ascending.
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
            if result.alignment_ratio is None:
                raise ValueError(
                    "A scored Technology Candidate "
                    "T2 result must have "
                    "alignment_ratio."
                )

            if (
                result.technology_alignment_score
                is None
            ):
                raise ValueError(
                    "A scored Technology Candidate "
                    "T2 result must have a "
                    "Technology Alignment score."
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
            -result.alignment_ratio,
            -result.matched_signal,
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


def score_profile_with_technology_candidate_2(
    *,
    student_proficiencies: Mapping[
        int,
        str,
    ],
) -> tuple[
    TechnologyCandidate2Result,
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

    idf_weights = (
        build_technology_idf_weights(
            requirements_by_career=(
                requirements_by_career
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
            calculate_technology_candidate_2_fit(
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
                idf_weights=(
                    idf_weights
                ),
                student_signal=(
                    student_signal
                ),
            )
        )

    return (
        rank_technology_candidate_2_results(
            results
        )
    )
