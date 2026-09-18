"""
Career context variants for GradNavi AI Candidate A2 validation.

A2 tests three focused semantic Career representations:

A2-I
    Career identity only.

A2-IE
    Career identity plus a compact summary of approved
    essential ESCO skills.

A2-IT
    Career identity plus a compact summary of approved
    O*NET In-Demand technologies.

A2 deliberately excludes O*NET numerical competencies from
semantic Career context.

Reason:

GradNavi already evaluates numerical competency evidence through
the dedicated Competency Fit component.

Technology evidence is included only in A2-IT as an experimental
candidate. The final semantic design will be selected by benchmark.

This module is experimental validation code only.
Production WBS 5.3 scoring is not modified.
"""

from dataclasses import dataclass
from enum import Enum

from careers.models import Career

from careers.scoring_validation.ai_semantic_context import (
    CareerSemanticEvidence,
    clean_semantic_text,
    format_decimal,
    load_career_semantic_evidence,
)


MAX_ESSENTIAL_ESCO_SKILLS = 12

MAX_IN_DEMAND_TECHNOLOGIES = 10


class AISemanticCandidate(
    str,
    Enum,
):
    """
    A2 Career semantic-context candidates.
    """

    IDENTITY = "a2_identity"

    IDENTITY_ESCO = (
        "a2_identity_essential_esco"
    )

    IDENTITY_TECHNOLOGY = (
        "a2_identity_technology"
    )


@dataclass(frozen=True)
class A2CareerContext:
    """
    One Career context for one A2 candidate.
    """

    career_id: int
    career_name: str

    candidate: AISemanticCandidate

    text: str

    essential_esco_count: int = 0

    technology_count: int = 0


def build_identity_lines(
    *,
    career: Career,
) -> list[str]:
    """
    Build the shared Career identity section.
    """

    if not career.active:
        raise ValueError(
            "A2 Career context requires "
            "an active Career."
        )

    lines = [
        "CAREER",
        "- name: "
        + clean_semantic_text(
            career.name
        ),
    ]

    category = clean_semantic_text(
        career.category
    )

    if category:
        lines.append(
            "- category: "
            + category
        )

    description = clean_semantic_text(
        career.description
    )

    if description:
        lines.append(
            "- description: "
            + description
        )

    return lines


def select_essential_esco(
    *,
    evidence: CareerSemanticEvidence,
) -> tuple:
    """
    Select a deterministic compact ESCO summary.

    Only source relationships labelled essential
    are eligible for A2-IE.
    """

    essential = [
        item
        for item
        in evidence.esco
        if (
            item.relation
            .strip()
            .casefold()
            == "essential"
        )
    ]

    essential.sort(
        key=lambda item: (
            item.skill_name.casefold(),
            item.concept_type.casefold(),
        )
    )

    return tuple(
        essential[
            :MAX_ESSENTIAL_ESCO_SKILLS
        ]
    )


def select_in_demand_technologies(
    *,
    evidence: CareerSemanticEvidence,
) -> tuple:
    """
    Select the strongest source-native O*NET
    In-Demand technologies.

    Evidence is ordered by higher demand percentage,
    then canonical Skill name.
    """

    ordered = sorted(
        evidence.technologies,
        key=lambda item: (
            -item.in_demand_percentage,
            item.skill_name.casefold(),
            item.concept_type.casefold(),
        ),
    )

    return tuple(
        ordered[
            :MAX_IN_DEMAND_TECHNOLOGIES
        ]
    )


def build_a2_identity_context(
    *,
    career: Career,
) -> A2CareerContext:
    """
    A2-I: Career identity only.
    """

    lines = build_identity_lines(
        career=career
    )

    return A2CareerContext(
        career_id=career.id,
        career_name=career.name,
        candidate=(
            AISemanticCandidate.IDENTITY
        ),
        text="\n".join(
            lines
        ),
    )


def build_a2_identity_esco_context(
    *,
    career: Career,
) -> A2CareerContext:
    """
    A2-IE: Career identity plus compact
    essential ESCO summary.
    """

    evidence = (
        load_career_semantic_evidence(
            career=career
        )
    )

    essential_esco = (
        select_essential_esco(
            evidence=evidence
        )
    )

    blocks = [
        "\n".join(
            build_identity_lines(
                career=career
            )
        )
    ]

    if essential_esco:
        lines = [
            "ESSENTIAL CAREER SKILLS",
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

    return A2CareerContext(
        career_id=career.id,
        career_name=career.name,
        candidate=(
            AISemanticCandidate
            .IDENTITY_ESCO
        ),
        text="\n\n".join(
            blocks
        ),
        essential_esco_count=len(
            essential_esco
        ),
    )


def build_a2_identity_technology_context(
    *,
    career: Career,
) -> A2CareerContext:
    """
    A2-IT: Career identity plus compact
    O*NET In-Demand technology summary.
    """

    evidence = (
        load_career_semantic_evidence(
            career=career
        )
    )

    technologies = (
        select_in_demand_technologies(
            evidence=evidence
        )
    )

    blocks = [
        "\n".join(
            build_identity_lines(
                career=career
            )
        )
    ]

    if technologies:
        lines = [
            "IN-DEMAND TECHNOLOGIES",
        ]

        for item in technologies:
            lines.append(
                "- "
                + clean_semantic_text(
                    item.skill_name
                )
                + " | demand: "
                + format_decimal(
                    item.in_demand_percentage
                )
                + "%"
            )

        blocks.append(
            "\n".join(
                lines
            )
        )

    return A2CareerContext(
        career_id=career.id,
        career_name=career.name,
        candidate=(
            AISemanticCandidate
            .IDENTITY_TECHNOLOGY
        ),
        text="\n\n".join(
            blocks
        ),
        technology_count=len(
            technologies
        ),
    )


def build_all_a2_contexts(
    *,
    career: Career,
) -> tuple[
    A2CareerContext,
    ...,
]:
    """
    Build all three A2 variants for one Career.
    """

    return (
        build_a2_identity_context(
            career=career
        ),
        build_a2_identity_esco_context(
            career=career
        ),
        build_a2_identity_technology_context(
            career=career
        ),
    )
