"""
Synthetic benchmark profiles for GradNavi Technology Candidate T1.

These profiles evaluate occupation-specific O*NET In-Demand
technology matching.

Important:

- Only Careers with at least one approved In-Demand technology
  receive benchmark profiles.
- Careers without In-Demand technology evidence are reported
  separately as unsupported by this scoring component.
- All synthetic technologies use Advanced proficiency so this
  benchmark isolates technology coverage and ranking behaviour.
- This is structural validation against the same reference data
  used by the scorer. It is not independent external validation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from careers.models import Career
from careers.scoring_validation.technology_candidate_1 import (
    TechnologyRequirement,
    load_in_demand_technologies_by_career,
)
from profiles.models import StudentSkill


class TechnologyBenchmarkScenario(
    str,
    Enum,
):
    """
    Structural Technology T1 benchmark scenarios.

    FULL_IN_DEMAND
        Student possesses every In-Demand technology for the
        target Career.

    HALF_IN_DEMAND
        Student possesses a deterministic half of the target
        Career's In-Demand technologies.

        O*NET provides a binary In-Demand signal here, not an
        importance ranking. The half is therefore selected from
        the deterministic technology ordering rather than being
        described as a "top" half.
    """

    FULL_IN_DEMAND = (
        "full_in_demand"
    )

    HALF_IN_DEMAND = (
        "half_in_demand"
    )


@dataclass(frozen=True)
class TechnologyBenchmarkSkill:
    """
    One technology in a synthetic Student profile.
    """

    skill_id: int
    skill_name: str
    proficiency_level: str


@dataclass(frozen=True)
class TechnologySyntheticBenchmarkProfile:
    """
    One synthetic technology profile with one expected Career.
    """

    target_career_id: int
    target_career_name: str

    scenario: TechnologyBenchmarkScenario

    skills: tuple[
        TechnologyBenchmarkSkill,
        ...
    ]

    target_requirement_count: int

    @property
    def student_proficiencies(
        self,
    ) -> dict[int, str]:
        """
        Return Skill ID -> GradNavi proficiency label.
        """

        return {
            skill.skill_id:
                skill.proficiency_level
            for skill in self.skills
        }


@dataclass(frozen=True)
class TechnologyBenchmarkCoverage:
    """
    Evidence coverage for the Technology T1 benchmark.
    """

    active_career_count: int

    supported_career_count: int
    unsupported_career_count: int

    supported_careers: tuple[
        str,
        ...
    ]

    unsupported_careers: tuple[
        str,
        ...
    ]


@dataclass(frozen=True)
class TechnologyBenchmarkDataset:
    """
    Complete synthetic dataset and evidence coverage.
    """

    profiles: tuple[
        TechnologySyntheticBenchmarkProfile,
        ...
    ]

    coverage: TechnologyBenchmarkCoverage


def take_deterministic_half(
    requirements: Iterable[
        TechnologyRequirement
    ],
) -> tuple[
    TechnologyRequirement,
    ...
]:
    """
    Keep a deterministic half of the technology requirements.

    For an odd number of technologies, the larger half is kept.

    Requirement ordering comes from the Technology T1 loader,
    which orders technologies by canonical Skill name and ID.
    """

    ordered = tuple(
        requirements
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


def build_technology_benchmark_profile(
    *,
    career: Career,
    scenario: TechnologyBenchmarkScenario,
    requirements: tuple[
        TechnologyRequirement,
        ...
    ],
) -> TechnologySyntheticBenchmarkProfile:
    """
    Build one deterministic Technology T1 benchmark profile.
    """

    if not career.active:
        raise ValueError(
            "Technology benchmark profiles require "
            "an active Career."
        )

    if not requirements:
        raise ValueError(
            "Technology benchmark profiles require at least "
            "one In-Demand technology."
        )

    if (
        scenario
        == TechnologyBenchmarkScenario.FULL_IN_DEMAND
    ):
        selected_requirements = (
            requirements
        )

    elif (
        scenario
        == TechnologyBenchmarkScenario.HALF_IN_DEMAND
    ):
        selected_requirements = (
            take_deterministic_half(
                requirements
            )
        )

    else:
        raise ValueError(
            "Unsupported Technology benchmark scenario: "
            f"{scenario!r}"
        )

    skills = tuple(
        TechnologyBenchmarkSkill(
            skill_id=(
                requirement.skill_id
            ),
            skill_name=(
                requirement.skill_name
            ),
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .ADVANCED
            ),
        )
        for requirement
        in selected_requirements
    )

    return TechnologySyntheticBenchmarkProfile(
        target_career_id=career.id,
        target_career_name=career.name,
        scenario=scenario,
        skills=skills,
        target_requirement_count=(
            len(requirements)
        ),
    )


def build_technology_benchmark_dataset(
    *,
    careers: tuple[
        Career,
        ...
    ] | None = None,
    requirements_by_career: Mapping[
        int,
        tuple[
            TechnologyRequirement,
            ...
        ],
    ] | None = None,
    scenarios: Iterable[
        TechnologyBenchmarkScenario
    ] | None = None,
) -> TechnologyBenchmarkDataset:
    """
    Build profiles for all Careers with usable In-Demand evidence.

    Unsupported Careers stay visible in coverage reporting but are
    excluded from ranking metrics.
    """

    if careers is None:
        selected_careers = tuple(
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
                "active",
            )
        )

    else:
        selected_careers = tuple(
            careers
        )

    if not selected_careers:
        raise ValueError(
            "At least one active Career is required."
        )

    career_ids = tuple(
        career.id
        for career in selected_careers
    )

    if requirements_by_career is None:
        loaded_requirements = (
            load_in_demand_technologies_by_career(
                career_ids=career_ids
            )
        )
    else:
        loaded_requirements = dict(
            requirements_by_career
        )

    if scenarios is None:
        selected_scenarios = (
            TechnologyBenchmarkScenario
            .FULL_IN_DEMAND,

            TechnologyBenchmarkScenario
            .HALF_IN_DEMAND,
        )
    else:
        selected_scenarios = tuple(
            scenarios
        )

    if not selected_scenarios:
        raise ValueError(
            "At least one Technology benchmark scenario "
            "is required."
        )

    supported = []
    unsupported = []
    profiles = []

    for career in selected_careers:
        requirements = tuple(
            loaded_requirements.get(
                career.id,
                (),
            )
        )

        if not requirements:
            unsupported.append(
                career.name
            )
            continue

        supported.append(
            career.name
        )

        for scenario in selected_scenarios:
            profiles.append(
                build_technology_benchmark_profile(
                    career=career,
                    scenario=scenario,
                    requirements=requirements,
                )
            )

    coverage = TechnologyBenchmarkCoverage(
        active_career_count=(
            len(selected_careers)
        ),
        supported_career_count=(
            len(supported)
        ),
        unsupported_career_count=(
            len(unsupported)
        ),
        supported_careers=tuple(
            supported
        ),
        unsupported_careers=tuple(
            unsupported
        ),
    )

    return TechnologyBenchmarkDataset(
        profiles=tuple(
            profiles
        ),
        coverage=coverage,
    )
