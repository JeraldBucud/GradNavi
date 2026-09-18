"""
Production Technology Fit service for GradNavi.

Locked WBS 5.3 Technology Fit design:

1. IDF-weighted Student Alignment.
2. O*NET demand-percentage-weighted Career Coverage.
3. Harmonic mean of both signals.

Student Alignment:

    matched_student_signal
    ----------------------
       student_signal

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

Only approved active O*NET Software Skills evidence marked
In Demand is eligible.

O*NET demand percentages stay on their source-native
0 to 100 scale.

This service performs database reads only.

Recommendation composite scoring and API serialization are
handled separately.
"""

from dataclasses import (
    dataclass,
    replace,
)
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)
from typing import (
    Iterable,
    Mapping,
)

from careers.models import (
    Career,
    CareerSkillEvidence,
    ReferenceDataset,
    ReviewStatus,
)

from careers.services.readiness_scoring import (
    map_student_proficiency,
)

from careers.services.recommendation_scoring import (
    ScoreStatus,
)

from profiles.models import StudentSkill


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
    One approved O*NET In-Demand technology requirement.
    """

    career_skill_id: int

    skill_id: int
    skill_name: str

    demand_percentage: Decimal


@dataclass(frozen=True)
class TechnologyIdfWeight:
    """
    Global discriminative weight for one technology.
    """

    skill_id: int
    skill_name: str

    document_frequency: int

    supported_career_count: int

    idf_weight: Decimal


@dataclass(frozen=True)
class TechnologyFitResult:
    """
    Production Technology Fit result for one Career.
    """

    career_id: int
    career_name: str

    score_status: ScoreStatus

    technology_fit_score: Decimal | None = None

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

    rank: int | None = None


def load_student_technology_proficiencies(
    *,
    student_profile_id: int,
) -> dict[int, str]:
    """
    Load canonical Student Skills with proficiency values.

    Recognition as a technology happens later through
    approved global O*NET In-Demand evidence.
    """

    if student_profile_id <= 0:
        raise ValueError(
            "student_profile_id must be "
            "greater than zero."
        )

    rows = (
        StudentSkill.objects
        .filter(
            student_profile_id=(
                student_profile_id
            )
        )
        .order_by(
            "skill_id"
        )
        .values_list(
            "skill_id",
            "proficiency_level",
        )
    )

    proficiencies = {}

    for (
        skill_id,
        proficiency_level,
    ) in rows:
        if skill_id in proficiencies:
            raise ValueError(
                "Duplicate Student Skill "
                "was loaded."
            )

        proficiencies[
            skill_id
        ] = proficiency_level

    return proficiencies


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

    requirements_by_career = {}

    seen_ids_by_career = {}

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
                "In-Demand O*NET technology "
                "is missing demand percentage: "
                f"Career {career_id}, "
                f"Skill {career_skill.skill.name}"
            )

        if not (
            SCORE_MINIMUM
            <= percentage
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "O*NET demand percentage "
                "must stay within 0 to 100."
            )

        seen_ids = (
            seen_ids_by_career
            .setdefault(
                career_id,
                set(),
            )
        )

        if (
            career_skill.id
            in seen_ids
        ):
            raise ValueError(
                "Duplicate demand-weighted "
                "technology evidence for "
                f"Career {career_id}."
            )

        seen_ids.add(
            career_skill.id
        )

        skill = (
            career_skill.skill
        )

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
        for (
            career_id,
            requirements,
        )
        in requirements_by_career.items()
    }


def build_technology_idf_weights(
    *,
    requirements_by_career: Mapping[
        int,
        Iterable[
            TechnologyDemandRequirement
        ],
    ],
) -> dict[
    int,
    TechnologyIdfWeight,
]:
    """
    Calculate global IDF-style technology weights.

    Formula:

        ln(
            (N + 1)
            /
            (df + 1)
        )
        + 1
    """

    supported_careers = {
        career_id: tuple(
            requirements
        )
        for (
            career_id,
            requirements,
        )
        in requirements_by_career.items()
        if tuple(
            requirements
        )
    }

    supported_career_count = len(
        supported_careers
    )

    if (
        supported_career_count
        == 0
    ):
        return {}

    career_ids_by_skill = {}

    skill_names = {}

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
                    "Duplicate In-Demand "
                    "technology within Career "
                    f"{career_id}."
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
                    "A canonical Skill ID "
                    "cannot have multiple names."
                )

            skill_names[
                requirement.skill_id
            ] = (
                requirement.skill_name
            )

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
            idf_weight=idf_weight,
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
    Calculate the Student's globally recognised
    technology signal.
    """

    signal = Decimal("0")

    for (
        skill_id,
        proficiency_level,
    ) in student_proficiencies.items():
        weight = (
            idf_weights.get(
                skill_id
            )
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
                "Mapped Student proficiency "
                "must stay within 0 to 100."
            )

        signal += (
            student_score
            * weight.idf_weight
        )

    return signal


def calculate_technology_fit(
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
) -> TechnologyFitResult:
    """
    Calculate the locked production T3 Technology Fit.
    """

    if career_id <= 0:
        raise ValueError(
            "career_id must be greater "
            "than zero."
        )

    if not career_name.strip():
        raise ValueError(
            "career_name must not be blank."
        )

    requirement_list = tuple(
        requirements
    )

    if not student_proficiencies:
        return TechnologyFitResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus
                .INSUFFICIENT_PROFILE
            ),
        )

    if not requirement_list:
        return TechnologyFitResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus
                .INSUFFICIENT_EVIDENCE
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

    if (
        student_signal
        <= SCORE_MINIMUM
    ):
        return TechnologyFitResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus
                .INSUFFICIENT_PROFILE
            ),
            career_requirement_count=len(
                requirement_list
            ),
        )

    seen_career_skill_ids = set()

    matched_student_signal = (
        Decimal("0")
    )

    matched_demand_signal = (
        Decimal("0")
    )

    total_demand_signal = (
        Decimal("0")
    )

    matched_names = []

    missing_names = []

    for requirement in (
        requirement_list
    ):
        if (
            requirement.career_skill_id
            in seen_career_skill_ids
        ):
            raise ValueError(
                "Duplicate demand-weighted "
                "technology requirement "
                "was supplied."
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

        weight = (
            idf_weights.get(
                requirement.skill_id
            )
        )

        if weight is None:
            raise ValueError(
                "Technology requirement "
                "is missing its global "
                "IDF weight: "
                f"{requirement.skill_name}"
            )

        proficiency_level = (
            student_proficiencies.get(
                requirement.skill_id
            )
        )

        if (
            proficiency_level
            is None
        ):
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
                "Mapped Student proficiency "
                "must stay within 0 to 100."
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

    if (
        total_demand_signal
        <= SCORE_MINIMUM
    ):
        return TechnologyFitResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus
                .INSUFFICIENT_EVIDENCE
            ),
            student_signal=(
                student_signal
            ),
            career_requirement_count=len(
                requirement_list
            ),
        )

    student_alignment_ratio = (
        matched_student_signal
        / student_signal
    )

    student_alignment_ratio = max(
        Decimal("0"),
        min(
            ONE,
            student_alignment_ratio,
        ),
    )

    demand_coverage_ratio = (
        matched_demand_signal
        / total_demand_signal
    )

    demand_coverage_ratio = max(
        Decimal("0"),
        min(
            ONE,
            demand_coverage_ratio,
        ),
    )

    if (
        student_alignment_ratio
        <= Decimal("0")
        or demand_coverage_ratio
        <= Decimal("0")
    ):
        technology_fit_ratio = (
            Decimal("0")
        )

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

    technology_fit_ratio = max(
        Decimal("0"),
        min(
            ONE,
            technology_fit_ratio,
        ),
    )

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

    return TechnologyFitResult(
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
        matched_technology_count=len(
            matched_technologies
        ),
        missing_technology_count=len(
            missing_technologies
        ),
        career_requirement_count=len(
            requirement_list
        ),
        matched_technologies=(
            matched_technologies
        ),
        missing_technologies=(
            missing_technologies
        ),
    )


def rank_technology_fit_results(
    results: Iterable[
        TechnologyFitResult
    ],
) -> tuple[
    TechnologyFitResult,
    ...
]:
    """
    Rank Technology Fit results deterministically.

    Tie breakers match validated Candidate T3.
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
                    "Scored Technology Fit "
                    "requires fit ratio."
                )

            if (
                result
                .demand_coverage_ratio
                is None
            ):
                raise ValueError(
                    "Scored Technology Fit "
                    "requires demand coverage."
                )

            if (
                result
                .student_alignment_ratio
                is None
            ):
                raise ValueError(
                    "Scored Technology Fit "
                    "requires Student alignment."
                )

            if (
                result
                .technology_fit_score
                is None
            ):
                raise ValueError(
                    "Scored Technology Fit "
                    "requires score."
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
        for (
            index,
            result,
        )
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


def score_technology_fit(
    *,
    student_profile_id: int,
) -> tuple[
    TechnologyFitResult,
    ...
]:
    """
    Score one Student Profile against all active Careers.

    Database reads only.
    """

    student_proficiencies = (
        load_student_technology_proficiencies(
            student_profile_id=(
                student_profile_id
            )
        )
    )

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
        for career
        in careers
    )

    requirements_by_career = (
        load_demand_weighted_technologies_by_career(
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
            calculate_technology_fit(
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
        rank_technology_fit_results(
            results
        )
    )
