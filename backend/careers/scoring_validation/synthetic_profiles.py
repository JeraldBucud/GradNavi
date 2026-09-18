"""
Synthetic Track A benchmark profiles for GradNavi.

These profiles evaluate recommendation scoring behaviour using
approved O*NET numerical competency evidence already present in
Dataset 1.0.

Important:
These are structural benchmark profiles derived from the same
occupational reference dataset used by the scorer. They are not
independent external validation.

Each synthetic Student receives the lowest GradNavi proficiency
category that satisfies the target Career's normalized O*NET Level.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Iterable

from careers.models import (
    Career,
    CareerSkillEvidence,
    ReferenceDataset,
    ReviewStatus,
)
from careers.services.recommendation_scoring import (
    ONET_NUMERICAL_SOURCE_DOMAINS,
    ONET_SOURCE_NAME,
)
from profiles.models import StudentSkill


PROFICIENCY_SCORES = {
    StudentSkill.ProficiencyLevel.FOUNDATIONAL:
        Decimal("25"),

    StudentSkill.ProficiencyLevel.DEVELOPING:
        Decimal("50"),

    StudentSkill.ProficiencyLevel.PROFICIENT:
        Decimal("75"),

    StudentSkill.ProficiencyLevel.ADVANCED:
        Decimal("100"),
}


class BenchmarkScenario(str, Enum):
    """
    Structural benchmark scenarios.

    FULL_COMPETENCY
        Student possesses every numerical competency for the
        target Career at the minimum GradNavi proficiency that
        satisfies the O*NET required Level.

    TOP_HALF_COMPETENCY
        Student possesses only the highest-Importance half of
        those competencies.
    """

    FULL_COMPETENCY = "full_competency"

    TOP_HALF_COMPETENCY = (
        "top_half_competency"
    )


@dataclass(frozen=True)
class BenchmarkSkill:
    """
    One canonical Skill in a synthetic Student profile.
    """

    skill_id: int
    skill_name: str
    concept_type: str

    proficiency_level: str

    importance: Decimal
    required_level: Decimal


@dataclass(frozen=True)
class SyntheticBenchmarkProfile:
    """
    One synthetic Student profile with one expected Career.
    """

    target_career_id: int
    target_career_name: str

    scenario: BenchmarkScenario

    skills: tuple[BenchmarkSkill, ...]

    @property
    def student_skill_ids(
        self,
    ) -> tuple[int, ...]:
        """
        Canonical IDs used by current WBS 5.3 V1.
        """

        return tuple(
            skill.skill_id
            for skill in self.skills
        )

    @property
    def student_proficiencies(
        self,
    ) -> dict[int, str]:
        """
        Skill ID -> GradNavi proficiency label.

        Candidate scoring models use this mapping.
        """

        return {
            skill.skill_id:
                skill.proficiency_level
            for skill in self.skills
        }


def proficiency_for_required_level(
    required_level: Decimal,
) -> str:
    """
    Return the lowest GradNavi proficiency category that satisfies
    an O*NET normalized required Level.

    GradNavi proficiency scale:

        Foundational = 25
        Developing   = 50
        Proficient   = 75
        Advanced     = 100
    """

    if (
        required_level <= Decimal("0")
        or required_level > Decimal("100")
    ):
        raise ValueError(
            "required_level must be greater than 0 "
            "and at most 100."
        )

    ordered_levels = (
        StudentSkill.ProficiencyLevel.FOUNDATIONAL,
        StudentSkill.ProficiencyLevel.DEVELOPING,
        StudentSkill.ProficiencyLevel.PROFICIENT,
        StudentSkill.ProficiencyLevel.ADVANCED,
    )

    for proficiency_level in ordered_levels:
        if (
            PROFICIENCY_SCORES[
                proficiency_level
            ]
            >= required_level
        ):
            return proficiency_level

    raise ValueError(
        "No GradNavi proficiency level could "
        "satisfy the required Level."
    )


def load_numerical_competencies(
    *,
    career_id: int,
) -> tuple[BenchmarkSkill, ...]:
    """
    Load approved numerical O*NET competency evidence.

    Both Importance and Level are required for the validation
    candidate models.
    """

    evidence_rows = (
        CareerSkillEvidence.objects
        .select_related(
            "career_skill__skill",
        )
        .filter(
            career_skill__career_id=career_id,
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
            not_relevant=False,
        )
        .exclude(
            recommend_suppress=True
        )
        .order_by(
            "-normalized_importance",
            "career_skill__skill__name",
            "career_skill__skill_id",
        )
    )

    seen_career_skill_ids = set()

    competencies = []

    for evidence in evidence_rows:
        career_skill = (
            evidence.career_skill
        )

        if (
            career_skill.id
            in seen_career_skill_ids
        ):
            raise ValueError(
                "Duplicate numerical CareerSkill evidence "
                f"for Career {career_id}: "
                f"{career_skill.id}"
            )

        seen_career_skill_ids.add(
            career_skill.id
        )

        skill = career_skill.skill

        required_level = (
            evidence.normalized_level
        )

        competencies.append(
            BenchmarkSkill(
                skill_id=skill.id,
                skill_name=skill.name,
                concept_type=(
                    skill.concept_type
                ),
                proficiency_level=(
                    proficiency_for_required_level(
                        required_level
                    )
                ),
                importance=(
                    evidence.normalized_importance
                ),
                required_level=(
                    required_level
                ),
            )
        )

    return tuple(
        competencies
    )


def take_top_half(
    skills: Iterable[BenchmarkSkill],
) -> tuple[BenchmarkSkill, ...]:
    """
    Keep the highest-Importance half.

    For odd-sized collections, the larger half is retained.
    """

    ordered = tuple(
        skills
    )

    if not ordered:
        return ()

    keep_count = max(
        1,
        (
            len(ordered)
            + 1
        )
        // 2,
    )

    return ordered[
        :keep_count
    ]


def build_benchmark_profile(
    *,
    career: Career,
    scenario: BenchmarkScenario,
    competencies: (
        tuple[BenchmarkSkill, ...]
        | None
    ) = None,
) -> SyntheticBenchmarkProfile:
    """
    Build one deterministic benchmark profile.
    """

    if not career.active:
        raise ValueError(
            "Benchmark profiles require "
            "an active Career."
        )

    if competencies is None:
        competencies = (
            load_numerical_competencies(
                career_id=career.id,
            )
        )

    if (
        scenario
        == BenchmarkScenario.FULL_COMPETENCY
    ):
        skills = competencies

    elif (
        scenario
        == BenchmarkScenario.TOP_HALF_COMPETENCY
    ):
        skills = take_top_half(
            competencies
        )

    else:
        raise ValueError(
            "Unsupported benchmark scenario: "
            f"{scenario!r}"
        )

    return SyntheticBenchmarkProfile(
        target_career_id=career.id,
        target_career_name=career.name,
        scenario=scenario,
        skills=skills,
    )


def build_all_benchmark_profiles(
    *,
    scenarios: Iterable[
        BenchmarkScenario
    ] | None = None,
) -> tuple[SyntheticBenchmarkProfile, ...]:
    """
    Generate benchmark profiles for every active Career.
    """

    if scenarios is None:
        selected_scenarios = (
            BenchmarkScenario.FULL_COMPETENCY,
            BenchmarkScenario.TOP_HALF_COMPETENCY,
        )

    else:
        selected_scenarios = tuple(
            scenarios
        )

    if not selected_scenarios:
        raise ValueError(
            "At least one benchmark scenario "
            "is required."
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
    )

    profiles = []

    for career in careers:
        competencies = (
            load_numerical_competencies(
                career_id=career.id,
            )
        )

        for scenario in selected_scenarios:
            profiles.append(
                build_benchmark_profile(
                    career=career,
                    scenario=scenario,
                    competencies=competencies,
                )
            )

    return tuple(
        profiles
    )