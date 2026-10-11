"""
Synthetic benchmark profiles for GradNavi AI Candidate A2.

The benchmark creates two deterministic scenarios for every
active Career using evidence-derived signals only.

Important benchmark rule:

The synthetic Student profile must not contain the expected
Career name, Career category, or Career description.

This avoids target-label leakage when evaluating semantic ranking.

FULL_SIGNAL
    Uses selected O*NET competencies, essential ESCO skills,
    and In-Demand technologies.

HALF_SIGNAL
    Uses a deterministic half of those same selected signals.

These profiles provide structural validation against GradNavi's
reference data.

They are not independent external validation.
"""

from dataclasses import dataclass
from enum import Enum

from careers.models import Career

from careers.scoring_validation.ai_candidate_2_contexts import (
    select_essential_esco,
    select_in_demand_technologies,
)

from careers.scoring_validation.ai_semantic_context import (
    clean_semantic_text,
    load_career_semantic_evidence,
)


MAX_BENCHMARK_NUMERICAL_COMPETENCIES = 12


class AISemanticBenchmarkScenario(
    str,
    Enum,
):
    FULL_SIGNAL = "full_signal"

    HALF_SIGNAL = "half_signal"


@dataclass(frozen=True)
class AISemanticSyntheticProfile:
    """
    One evidence-derived synthetic Student profile.
    """

    target_career_id: int
    target_career_name: str

    scenario: AISemanticBenchmarkScenario

    text: str

    numerical_competency_count: int
    essential_esco_count: int
    technology_count: int


@dataclass(frozen=True)
class AISemanticBenchmarkDataset:
    """
    Complete A2 synthetic benchmark dataset.
    """

    profiles: tuple[
        AISemanticSyntheticProfile,
        ...
    ]

    active_career_count: int


def take_deterministic_half(
    items: tuple,
) -> tuple:
    """
    Keep the larger deterministic half.

    Existing item ordering is preserved.
    """

    if not items:
        return ()

    keep_count = max(
        1,
        (
            len(items)
            + 1
        )
        // 2,
    )

    return items[
        :keep_count
    ]


def select_numerical_competencies(
    *,
    evidence,
) -> tuple:
    """
    Select a compact O*NET competency summary.

    load_career_semantic_evidence already orders numerical evidence
    by higher normalized importance, then canonical Skill name.
    """

    return tuple(
        evidence.numerical[
            :MAX_BENCHMARK_NUMERICAL_COMPETENCIES
        ]
    )


def build_evidence_student_text(
    *,
    numerical_competencies: tuple,
    essential_esco: tuple,
    technologies: tuple,
) -> str:
    """
    Build synthetic Student text without target Career metadata.
    """

    blocks = [
        "STUDENT CAREER PROFILE"
    ]

    if numerical_competencies:
        lines = [
            "COMPETENCIES",
        ]

        for item in numerical_competencies:
            lines.append(
                "- "
                + clean_semantic_text(
                    item.skill_name
                )
            )

        blocks.append(
            "\n".join(
                lines
            )
        )

    if essential_esco:
        lines = [
            "SKILLS",
        ]

        for item in essential_esco:
            lines.append(
                "- "
                + clean_semantic_text(
                    item.skill_name
                )
            )

        blocks.append(
            "\n".join(
                lines
            )
        )

    if technologies:
        lines = [
            "TECHNOLOGIES",
        ]

        for item in technologies:
            lines.append(
                "- "
                + clean_semantic_text(
                    item.skill_name
                )
            )

        blocks.append(
            "\n".join(
                lines
            )
        )

    return "\n\n".join(
        blocks
    )


FORBIDDEN_STUDENT_METADATA_LINES = frozenset(
    {
        "career",
        "career identity",
        "career goal",
        "career goals",
    }
)

FORBIDDEN_STUDENT_METADATA_PREFIXES = (
    "- name:",
    "- category:",
    "- description:",
    "- career name:",
    "- career category:",
    "- career description:",
    "- target role:",
    "- target field:",
    "- goal description:",
)


def validate_no_injected_career_metadata(
    *,
    text: str,
) -> None:
    """
    Reject structurally injected Career metadata.

    Legitimate evidence is allowed to contain terms that overlap
    naturally with a Career name or category.

    Examples of valid evidence include:

    - civil engineering
    - cyber security
    - Engineering and Technology
    - communicate in healthcare

    The guard instead rejects explicit Career metadata fields such
    as target role, category, description, or Career identity blocks.
    """

    for raw_line in text.splitlines():
        normalized_line = (
            clean_semantic_text(
                raw_line
            )
            .casefold()
        )

        if (
            normalized_line
            in FORBIDDEN_STUDENT_METADATA_LINES
        ):
            raise ValueError(
                "Synthetic A2 profile contains "
                "injected Career metadata."
            )

        if any(
            normalized_line.startswith(
                prefix
            )
            for prefix
            in FORBIDDEN_STUDENT_METADATA_PREFIXES
        ):
            raise ValueError(
                "Synthetic A2 profile contains "
                "injected Career metadata."
            )


def build_a2_synthetic_profile(
    *,
    career: Career,
    scenario: AISemanticBenchmarkScenario,
) -> AISemanticSyntheticProfile:
    """
    Build one deterministic evidence-derived benchmark profile.
    """

    if not career.active:
        raise ValueError(
            "A2 benchmark profile requires "
            "an active Career."
        )

    evidence = (
        load_career_semantic_evidence(
            career=career
        )
    )

    numerical_competencies = (
        select_numerical_competencies(
            evidence=evidence
        )
    )

    essential_esco = (
        select_essential_esco(
            evidence=evidence
        )
    )

    technologies = (
        select_in_demand_technologies(
            evidence=evidence
        )
    )

    if (
        scenario
        == AISemanticBenchmarkScenario.FULL_SIGNAL
    ):
        selected_numerical = (
            numerical_competencies
        )

        selected_esco = (
            essential_esco
        )

        selected_technologies = (
            technologies
        )

    elif (
        scenario
        == AISemanticBenchmarkScenario.HALF_SIGNAL
    ):
        selected_numerical = (
            take_deterministic_half(
                numerical_competencies
            )
        )

        selected_esco = (
            take_deterministic_half(
                essential_esco
            )
        )

        selected_technologies = (
            take_deterministic_half(
                technologies
            )
        )

    else:
        raise ValueError(
            "Unsupported A2 benchmark scenario: "
            f"{scenario!r}"
        )

    text = build_evidence_student_text(
        numerical_competencies=(
            selected_numerical
        ),
        essential_esco=(
            selected_esco
        ),
        technologies=(
            selected_technologies
        ),
    )

    validate_no_injected_career_metadata(
        text=text
    )

    return AISemanticSyntheticProfile(
        target_career_id=career.id,
        target_career_name=career.name,
        scenario=scenario,
        text=text,
        numerical_competency_count=len(
            selected_numerical
        ),
        essential_esco_count=len(
            selected_esco
        ),
        technology_count=len(
            selected_technologies
        ),
    )


def build_a2_benchmark_dataset(
) -> AISemanticBenchmarkDataset:
    """
    Build two benchmark cases for every active Career.
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
    )

    if not careers:
        raise ValueError(
            "No active Careers are available."
        )

    profiles = []

    for career in careers:
        for scenario in (
            AISemanticBenchmarkScenario.FULL_SIGNAL,
            AISemanticBenchmarkScenario.HALF_SIGNAL,
        ):
            profiles.append(
                build_a2_synthetic_profile(
                    career=career,
                    scenario=scenario,
                )
            )

    return AISemanticBenchmarkDataset(
        profiles=tuple(
            profiles
        ),
        active_career_count=len(
            careers
        ),
    )
