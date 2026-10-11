"""
GradNavi AI Candidate A3 semantic scoring.

A3 keeps AI Semantic Alignment independent from the dedicated
Technology Fit component.

A3 combines two semantic signals:

1. Career Identity similarity.
2. Essential ESCO Skill similarity.

Four fixed weighting candidates are evaluated:

A3-90
    90% Career Identity
    10% Essential ESCO

A3-80
    80% Career Identity
    20% Essential ESCO

A3-70
    70% Career Identity
    30% Essential ESCO

A3-60
    60% Career Identity
    40% Essential ESCO

If a Career has no approved essential ESCO evidence,
Career Identity receives 100% of the semantic weight.

Technology evidence is deliberately excluded from A3.

This keeps AI Semantic Alignment separate from GradNavi's
Technology Fit score.

This module is experimental validation code only.
Production WBS 5.3 scoring is not modified.
"""

from dataclasses import (
    dataclass,
    replace,
)
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)
from enum import Enum
from typing import Iterable

from careers.models import Career

from careers.scoring_validation.ai_candidate_2_contexts import (
    build_a2_identity_context,
    select_essential_esco,
)

from careers.scoring_validation.ai_semantic_context import (
    clean_semantic_text,
    load_career_semantic_evidence,
)


SCORE_MAXIMUM = Decimal("100")

SCORE_QUANTUM = Decimal("0.01")

RATIO_QUANTUM = Decimal("0.000001")


class A3WeightingCandidate(
    str,
    Enum,
):
    IDENTITY_90_ESCO_10 = (
        "a3_identity_90_esco_10"
    )

    IDENTITY_80_ESCO_20 = (
        "a3_identity_80_esco_20"
    )

    IDENTITY_70_ESCO_30 = (
        "a3_identity_70_esco_30"
    )

    IDENTITY_60_ESCO_40 = (
        "a3_identity_60_esco_40"
    )


A3_WEIGHTS = {
    A3WeightingCandidate
    .IDENTITY_90_ESCO_10: (
        Decimal("0.90"),
        Decimal("0.10"),
    ),

    A3WeightingCandidate
    .IDENTITY_80_ESCO_20: (
        Decimal("0.80"),
        Decimal("0.20"),
    ),

    A3WeightingCandidate
    .IDENTITY_70_ESCO_30: (
        Decimal("0.70"),
        Decimal("0.30"),
    ),

    A3WeightingCandidate
    .IDENTITY_60_ESCO_40: (
        Decimal("0.60"),
        Decimal("0.40"),
    ),
}


@dataclass(frozen=True)
class A3CareerContexts:
    """
    Separate Career semantic contexts used by A3.
    """

    career_id: int
    career_name: str

    identity_text: str

    essential_esco_text: str | None

    essential_esco_count: int


@dataclass(frozen=True)
class A3CareerResult:
    """
    One A3 semantic result for one Career.
    """

    career_id: int
    career_name: str

    candidate: A3WeightingCandidate

    identity_similarity: Decimal

    esco_similarity: Decimal | None

    semantic_alignment_ratio: Decimal

    semantic_alignment_score: Decimal

    rank: int | None = None


def build_a3_career_contexts(
    *,
    career: Career,
) -> A3CareerContexts:
    """
    Build separate Identity and Essential ESCO contexts.
    """

    identity = build_a2_identity_context(
        career=career
    )

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

    esco_text = None

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

        esco_text = "\n".join(
            lines
        )

    return A3CareerContexts(
        career_id=career.id,
        career_name=career.name,
        identity_text=identity.text,
        essential_esco_text=esco_text,
        essential_esco_count=len(
            essential_esco
        ),
    )


def clamp_semantic_similarity(
    similarity: Decimal,
) -> Decimal:
    """
    Convert negative semantic similarity to zero.

    A similarity above one is rejected.
    """

    if similarity > Decimal("1"):
        raise ValueError(
            "Semantic similarity must not "
            "exceed one."
        )

    if similarity < Decimal("-1"):
        raise ValueError(
            "Semantic similarity must not "
            "be below negative one."
        )

    return max(
        Decimal("0"),
        similarity,
    )


def combine_a3_semantic_similarity(
    *,
    identity_similarity: Decimal,
    esco_similarity: Decimal | None,
    candidate: A3WeightingCandidate,
) -> Decimal:
    """
    Combine A3 Identity and ESCO similarities.

    Missing ESCO evidence falls back to
    100% Career Identity similarity.
    """

    identity_signal = (
        clamp_semantic_similarity(
            identity_similarity
        )
    )

    if esco_similarity is None:
        return identity_signal.quantize(
            RATIO_QUANTUM,
            rounding=ROUND_HALF_UP,
        )

    esco_signal = (
        clamp_semantic_similarity(
            esco_similarity
        )
    )

    (
        identity_weight,
        esco_weight,
    ) = A3_WEIGHTS[
        candidate
    ]

    if (
        identity_weight
        + esco_weight
        != Decimal("1")
    ):
        raise ValueError(
            "A3 semantic weights must sum to one."
        )

    combined = (
        identity_signal
        * identity_weight
        + esco_signal
        * esco_weight
    )

    return combined.quantize(
        RATIO_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def build_a3_result(
    *,
    career_id: int,
    career_name: str,
    candidate: A3WeightingCandidate,
    identity_similarity: Decimal,
    esco_similarity: Decimal | None,
) -> A3CareerResult:
    """
    Build one scored A3 Career result.
    """

    ratio = (
        combine_a3_semantic_similarity(
            identity_similarity=(
                identity_similarity
            ),
            esco_similarity=(
                esco_similarity
            ),
            candidate=candidate,
        )
    )

    score = (
        ratio
        * SCORE_MAXIMUM
    ).quantize(
        SCORE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )

    return A3CareerResult(
        career_id=career_id,
        career_name=career_name,
        candidate=candidate,
        identity_similarity=(
            identity_similarity
        ),
        esco_similarity=(
            esco_similarity
        ),
        semantic_alignment_ratio=ratio,
        semantic_alignment_score=score,
    )


def rank_a3_results(
    results: Iterable[
        A3CareerResult
    ],
) -> tuple[
    A3CareerResult,
    ...
]:
    """
    Rank A3 results deterministically.

    Tie breakers:

    1. Higher semantic ratio.
    2. Career name alphabetically.
    3. Career ID ascending.
    """

    ordered = list(
        results
    )

    ordered.sort(
        key=lambda result: (
            -result.semantic_alignment_ratio,
            result.career_name.casefold(),
            result.career_id,
        )
    )

    return tuple(
        replace(
            result,
            rank=rank,
        )
        for rank, result
        in enumerate(
            ordered,
            start=1,
        )
    )
