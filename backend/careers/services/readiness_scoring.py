"""
Deterministic Skill Gap and Career Readiness scoring for GradNavi.

WBS 5.5 compares Student proficiency with source-backed O*NET
Career requirement levels.

This module begins with pure scoring structures and calculations.
Database loading and orchestration are added separately.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Iterable, Mapping

from careers.models import (
    Career,
    CareerSkillEvidence,
    ReferenceDataset,
    ReviewStatus,
)
from profiles.models import StudentSkill


SCORE_MINIMUM = Decimal("0")
SCORE_MAXIMUM = Decimal("100")
SCORE_QUANTUM = Decimal("0.01")
ATTAINMENT_MAXIMUM = Decimal("1")

ONET_SOURCE_NAME = "O*NET Database"

ONET_NUMERICAL_SOURCE_DOMAINS = (
    "onet_essential_skills",
    "onet_knowledge",
    "onet_transferable_skills",
)

READINESS_CONCEPT_TYPES = (
    "skill",
    "knowledge",
)

PROFICIENCY_SCORES = {
    "foundational": Decimal("25"),
    "developing": Decimal("50"),
    "proficient": Decimal("75"),
    "advanced": Decimal("100"),
}


class ReadinessScoringError(Exception):
    """
    Base exception for WBS 5.5 readiness service errors.
    """


class CareerNotFoundError(ReadinessScoringError):
    """
    Raised when the requested Career does not exist.
    """


class CareerNotAvailableError(ReadinessScoringError):
    """
    Raised when the requested Career exists but is inactive.
    """


class ReadinessStatus(str, Enum):
    """
    Describes whether a Career received a valid readiness score.
    """

    SCORED = "scored"
    INSUFFICIENT_PROFILE = "insufficient_profile"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class GapStatus(str, Enum):
    """
    Describes the Student's status for one Career requirement.
    """

    MISSING = "missing"
    BELOW_REQUIREMENT = "below_requirement"
    MEETS_REQUIREMENT = "meets_requirement"


@dataclass(frozen=True)
class CareerReadinessRequirement:
    """
    One source-backed Career requirement used by WBS 5.5.

    importance
        O*NET normalized Importance from 0 to 100.

    required_level
        O*NET normalized Level greater than 0 and at most 100.
    """

    career_skill_id: int
    skill_id: int
    skill_name: str
    concept_type: str
    source_domain: str
    importance: Decimal
    required_level: Decimal


@dataclass(frozen=True)
class SkillGapResult:
    """
    Readiness and Skill Gap result for one Career requirement.
    """

    career_skill_id: int
    skill_id: int
    skill_name: str
    concept_type: str
    source_domain: str

    student_proficiency_level: str | None
    student_proficiency_score: Decimal

    required_level: Decimal
    importance: Decimal

    gap_amount: Decimal
    attainment_ratio: Decimal
    attainment_percentage: Decimal
    weighted_contribution: Decimal

    gap_status: GapStatus


@dataclass(frozen=True)
class CareerReadinessResult:
    """
    Structured WBS 5.5 result for one selected Career.
    """

    career_id: int
    career_name: str
    score_status: ReadinessStatus

    readiness_score: Decimal | None = None

    matched_requirement_count: int = 0
    missing_requirement_count: int = 0
    below_requirement_count: int = 0
    meets_requirement_count: int = 0

    total_importance_weight: Decimal = Decimal("0")
    weighted_attainment: Decimal = Decimal("0")

    skill_gaps: tuple[SkillGapResult, ...] = ()


def map_student_proficiency(
    proficiency_level: str | None,
) -> Decimal:
    """
    Convert a GradNavi Student proficiency label to 0 to 100.

    Missing Student Skill:
        0

    Foundational:
        25

    Developing:
        50

    Proficient:
        75

    Advanced:
        100
    """

    if proficiency_level is None:
        return Decimal("0")

    try:
        return PROFICIENCY_SCORES[
            proficiency_level
        ]

    except KeyError as exc:
        raise ValueError(
            "Unsupported Student proficiency level: "
            f"{proficiency_level!r}"
        ) from exc


def _validate_requirement(
    requirement: CareerReadinessRequirement,
) -> None:
    """
    Validate one Career requirement before readiness calculation.
    """

    if requirement.career_skill_id <= 0:
        raise ValueError(
            "career_skill_id must be greater than zero."
        )

    if requirement.skill_id <= 0:
        raise ValueError(
            "skill_id must be greater than zero."
        )

    if not requirement.skill_name.strip():
        raise ValueError(
            "skill_name must not be blank."
        )

    if (
        requirement.concept_type
        not in READINESS_CONCEPT_TYPES
    ):
        raise ValueError(
            "Unsupported readiness concept type: "
            f"{requirement.concept_type!r}"
        )

    if (
        requirement.source_domain
        not in ONET_NUMERICAL_SOURCE_DOMAINS
    ):
        raise ValueError(
            "Unsupported readiness source domain: "
            f"{requirement.source_domain!r}"
        )

    if not (
        SCORE_MINIMUM
        <= requirement.importance
        <= SCORE_MAXIMUM
    ):
        raise ValueError(
            "Importance must stay within 0 to 100."
        )

    if not (
        SCORE_MINIMUM
        < requirement.required_level
        <= SCORE_MAXIMUM
    ):
        raise ValueError(
            "Required Level must be greater than 0 "
            "and at most 100."
        )


def order_skill_gaps(
    skill_gaps: Iterable[SkillGapResult],
) -> tuple[SkillGapResult, ...]:
    """
    Order WBS 5.5 Skill Gap results deterministically.

    Priority:

    1. Missing Skills.
    2. Below-requirement Skills.
    3. Skills meeting requirements.
    4. Higher Importance first.
    5. Larger gap first.
    6. Skill name alphabetically.
    7. Skill ID ascending.
    """

    status_priority = {
        GapStatus.MISSING: 0,
        GapStatus.BELOW_REQUIREMENT: 1,
        GapStatus.MEETS_REQUIREMENT: 2,
    }

    return tuple(
        sorted(
            skill_gaps,
            key=lambda gap: (
                status_priority[
                    gap.gap_status
                ],
                -gap.importance,
                -gap.gap_amount,
                gap.skill_name.casefold(),
                gap.skill_id,
            ),
        )
    )


def calculate_skill_gap(
    *,
    requirement: CareerReadinessRequirement,
    student_proficiency_level: str | None,
) -> SkillGapResult:
    """
    Calculate readiness for one Career requirement.

    This function performs no database operations.
    """

    _validate_requirement(
        requirement
    )

    student_score = (
        map_student_proficiency(
            student_proficiency_level
        )
    )

    raw_attainment = (
        student_score
        / requirement.required_level
    )

    attainment_ratio = min(
        raw_attainment,
        ATTAINMENT_MAXIMUM,
    )

    attainment_percentage = (
        attainment_ratio
        * SCORE_MAXIMUM
    ).quantize(
        SCORE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )

    gap_amount = max(
        (
            requirement.required_level
            - student_score
        ),
        SCORE_MINIMUM,
    ).quantize(
        SCORE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )

    weighted_contribution = (
        requirement.importance
        * attainment_ratio
    )

    if student_proficiency_level is None:
        gap_status = GapStatus.MISSING

    elif (
        student_score
        < requirement.required_level
    ):
        gap_status = (
            GapStatus.BELOW_REQUIREMENT
        )

    else:
        gap_status = (
            GapStatus.MEETS_REQUIREMENT
        )

    return SkillGapResult(
        career_skill_id=(
            requirement.career_skill_id
        ),
        skill_id=requirement.skill_id,
        skill_name=requirement.skill_name,
        concept_type=requirement.concept_type,
        source_domain=requirement.source_domain,
        student_proficiency_level=(
            student_proficiency_level
        ),
        student_proficiency_score=(
            student_score
        ),
        required_level=(
            requirement.required_level
        ),
        importance=requirement.importance,
        gap_amount=gap_amount,
        attainment_ratio=(
            attainment_ratio
        ),
        attainment_percentage=(
            attainment_percentage
        ),
        weighted_contribution=(
            weighted_contribution
        ),
        gap_status=gap_status,
    )


def calculate_career_readiness(
    *,
    career_id: int,
    career_name: str,
    student_proficiencies: Mapping[int, str],
    requirements: Iterable[CareerReadinessRequirement],
) -> CareerReadinessResult:
    """
    Calculate WBS 5.5 readiness for one selected Career.

    student_proficiencies maps canonical Skill IDs to the
    StudentSkill proficiency label stored by GradNavi.

    This function performs no database operations.
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

    # An empty Student Skill profile means GradNavi does not
    # have enough Student evidence to report zero readiness.
    if not student_proficiencies:
        return CareerReadinessResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ReadinessStatus
                .INSUFFICIENT_PROFILE
            ),
        )

    # A Career without source-backed readiness evidence must
    # not receive a misleading zero score.
    if not requirement_list:
        return CareerReadinessResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ReadinessStatus
                .INSUFFICIENT_EVIDENCE
            ),
        )

    seen_career_skill_ids = set()

    skill_gaps = []

    for requirement in requirement_list:
        if (
            requirement.career_skill_id
            in seen_career_skill_ids
        ):
            raise ValueError(
                "Duplicate CareerSkill readiness "
                "evidence is not allowed."
            )

        seen_career_skill_ids.add(
            requirement.career_skill_id
        )

        student_proficiency_level = (
            student_proficiencies.get(
                requirement.skill_id
            )
        )

        skill_gaps.append(
            calculate_skill_gap(
                requirement=requirement,
                student_proficiency_level=(
                    student_proficiency_level
                ),
            )
        )

    ordered_skill_gaps = (
        order_skill_gaps(
            skill_gaps
        )
    )

    total_importance_weight = sum(
        (
            gap.importance
            for gap in ordered_skill_gaps
        ),
        Decimal("0"),
    )

    weighted_attainment = sum(
        (
            gap.weighted_contribution
            for gap in ordered_skill_gaps
        ),
        Decimal("0"),
    )

    missing_requirement_count = sum(
        gap.gap_status
        == GapStatus.MISSING
        for gap in ordered_skill_gaps
    )

    below_requirement_count = sum(
        gap.gap_status
        == GapStatus.BELOW_REQUIREMENT
        for gap in ordered_skill_gaps
    )

    meets_requirement_count = sum(
        gap.gap_status
        == GapStatus.MEETS_REQUIREMENT
        for gap in ordered_skill_gaps
    )

    matched_requirement_count = (
        below_requirement_count
        + meets_requirement_count
    )

    if (
        total_importance_weight
        <= SCORE_MINIMUM
    ):
        return CareerReadinessResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ReadinessStatus
                .INSUFFICIENT_EVIDENCE
            ),
            matched_requirement_count=(
                matched_requirement_count
            ),
            missing_requirement_count=(
                missing_requirement_count
            ),
            below_requirement_count=(
                below_requirement_count
            ),
            meets_requirement_count=(
                meets_requirement_count
            ),
            total_importance_weight=(
                total_importance_weight
            ),
            weighted_attainment=(
                weighted_attainment
            ),
            skill_gaps=(
                ordered_skill_gaps
            ),
        )

    readiness_score = (
        (
            weighted_attainment
            / total_importance_weight
        )
        * SCORE_MAXIMUM
    ).quantize(
        SCORE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )

    if not (
        SCORE_MINIMUM
        <= readiness_score
        <= SCORE_MAXIMUM
    ):
        raise ValueError(
            "Career Readiness Score must stay "
            "within 0 to 100."
        )

    return CareerReadinessResult(
        career_id=career_id,
        career_name=career_name,
        score_status=(
            ReadinessStatus.SCORED
        ),
        readiness_score=(
            readiness_score
        ),
        matched_requirement_count=(
            matched_requirement_count
        ),
        missing_requirement_count=(
            missing_requirement_count
        ),
        below_requirement_count=(
            below_requirement_count
        ),
        meets_requirement_count=(
            meets_requirement_count
        ),
        total_importance_weight=(
            total_importance_weight
        ),
        weighted_attainment=(
            weighted_attainment
        ),
        skill_gaps=(
            ordered_skill_gaps
        ),
    )


def load_student_proficiencies(
    *,
    student_profile_id: int,
) -> dict[int, str]:
    """
    Load canonical Student Skill IDs and proficiency labels.

    The returned mapping uses:

    canonical Skill ID -> StudentSkill proficiency value

    This function performs database reads only.
    """

    if student_profile_id <= 0:
        raise ValueError(
            "student_profile_id must be greater than zero."
        )

    return dict(
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


def load_career_readiness_requirements(
    *,
    career_id: int,
) -> tuple[CareerReadinessRequirement, ...]:
    """
    Load eligible WBS 5.5 O*NET readiness evidence.

    Version 1 requirements must:

    - Belong to the selected Career.
    - Use an approved CareerSkill.
    - Belong to an active ReferenceDataset.
    - Come from O*NET Database.
    - Use an approved numerical source domain.
    - Have normalized Importance.
    - Have normalized Level.
    - Use Skill or Knowledge concepts.
    - Not be marked not relevant.
    - Not be marked recommend suppress.

    Duplicate CareerSkill evidence remains visible so the pure
    Career readiness function rejects accidental double counting.

    This function performs database reads only.
    """

    if career_id <= 0:
        raise ValueError(
            "career_id must be greater than zero."
        )

    evidence_rows = (
        CareerSkillEvidence.objects
        .select_related(
            "career_skill__skill",
        )
        .filter(
            career_skill__career_id=(
                career_id
            ),
            career_skill__review_status=(
                ReviewStatus.APPROVED
            ),
            career_skill__skill__concept_type__in=(
                READINESS_CONCEPT_TYPES
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
            not_relevant=False,
        )
        .exclude(
            recommend_suppress=True
        )
        .order_by(
            "career_skill_id",
            "id",
        )
    )

    return tuple(
        CareerReadinessRequirement(
            career_skill_id=(
                evidence.career_skill_id
            ),
            skill_id=(
                evidence
                .career_skill
                .skill_id
            ),
            skill_name=(
                evidence
                .career_skill
                .skill
                .name
            ),
            concept_type=(
                evidence
                .career_skill
                .skill
                .concept_type
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
        for evidence in evidence_rows
    )


def calculate_selected_career_readiness(
    *,
    student_profile_id: int,
    career_id: int,
) -> CareerReadinessResult:
    """
    Calculate WBS 5.5 readiness for one selected active Career.

    This orchestration function connects:

    1. Career availability validation.
    2. Student proficiency loading.
    3. Career readiness evidence loading.
    4. Pure Career readiness calculation.

    The function performs database reads only.
    """

    if student_profile_id <= 0:
        raise ValueError(
            "student_profile_id must be greater than zero."
        )

    if career_id <= 0:
        raise ValueError(
            "career_id must be greater than zero."
        )

    career = (
        Career.objects
        .filter(
            id=career_id
        )
        .only(
            "id",
            "name",
            "active",
        )
        .first()
    )

    if career is None:
        raise CareerNotFoundError(
            f"Career {career_id} does not exist."
        )

    if not career.active:
        raise CareerNotAvailableError(
            f"Career {career_id} is not active."
        )

    student_proficiencies = (
        load_student_proficiencies(
            student_profile_id=(
                student_profile_id
            )
        )
    )

    requirements = (
        load_career_readiness_requirements(
            career_id=career.id
        )
    )

    return calculate_career_readiness(
        career_id=career.id,
        career_name=career.name,
        student_proficiencies=(
            student_proficiencies
        ),
        requirements=requirements,
    )
