"""
Diagnostics for the GradNavi WBS 5.3 Version 1 scorer.

This module explains structural failure modes of the current
recommendation model before candidate formulas are introduced.

It measures:

- numerical-evidence coverage by Career;
- how widely each competency occurs across Careers;
- score saturation for full target-Career profiles;
- Career competency-set containment;
- which Careers repeatedly tie at 100%.

No database rows are modified.
"""

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal

from careers.models import Career
from careers.services.recommendation_scoring import (
    RecommendationResult,
    calculate_career_fit,
    load_weighted_competencies_by_career,
    rank_recommendation_results,
)


@dataclass(frozen=True)
class CompetencyFrequency:
    """
    How broadly one canonical competency occurs across Careers.
    """

    skill_id: int
    skill_name: str

    career_count: int
    career_share: Decimal


@dataclass(frozen=True)
class CareerSaturationDiagnostic:
    """
    V1 behaviour for a profile containing every numerical
    competency of one target Career.
    """

    career_id: int
    career_name: str

    competency_count: int

    target_rank: int | None
    target_score: Decimal | None

    perfect_score_count: int

    perfect_score_careers: tuple[
        str,
        ...
    ]

    subset_career_count: int

    subset_careers: tuple[
        str,
        ...
    ]


@dataclass(frozen=True)
class V1DiagnosticReport:
    """
    Structural diagnostic report for the V1 recommendation model.
    """

    active_career_count: int

    career_count_with_evidence: int

    career_count_without_evidence: int

    careers_without_evidence: tuple[
        str,
        ...
    ]

    competency_frequencies: tuple[
        CompetencyFrequency,
        ...
    ]

    saturation_diagnostics: tuple[
        CareerSaturationDiagnostic,
        ...
    ]


def _score_skill_set(
    *,
    student_skill_ids: tuple[int, ...],
    careers: tuple[Career, ...],
    competencies_by_career: dict,
) -> tuple[
    RecommendationResult,
    ...
]:
    """
    Score an in-memory Skill set using untouched production V1.
    """

    results = []

    for career in careers:
        result = calculate_career_fit(
            career_id=career.id,
            career_name=career.name,
            student_skill_ids=(
                student_skill_ids
            ),
            weighted_competencies=(
                competencies_by_career.get(
                    career.id,
                    (),
                )
            ),
        )

        results.append(
            result
        )

    return rank_recommendation_results(
        results
    )


def run_v1_diagnostics() -> V1DiagnosticReport:
    """
    Run structural diagnostics over all active GradNavi Careers.
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
        raise ValueError(
            "No active Careers are available."
        )

    career_ids = tuple(
        career.id
        for career in careers
    )

    competencies_by_career = (
        load_weighted_competencies_by_career(
            career_ids=career_ids,
        )
    )

    career_skill_sets = {}

    skill_names = {}

    skill_career_counts = Counter()

    careers_without_evidence = []

    for career in careers:
        competencies = (
            competencies_by_career.get(
                career.id,
                (),
            )
        )

        skill_ids = frozenset(
            competency.skill_id
            for competency in competencies
        )

        career_skill_sets[
            career.id
        ] = skill_ids

        if not skill_ids:
            careers_without_evidence.append(
                career.name
            )

        for competency in competencies:
            skill_names[
                competency.skill_id
            ] = competency.skill_name

        for skill_id in skill_ids:
            skill_career_counts[
                skill_id
            ] += 1

    active_career_count = len(
        careers
    )

    competency_frequencies = []

    for (
        skill_id,
        career_count,
    ) in skill_career_counts.items():
        career_share = (
            Decimal(career_count)
            / Decimal(active_career_count)
            * Decimal("100")
        ).quantize(
            Decimal("0.01")
        )

        competency_frequencies.append(
            CompetencyFrequency(
                skill_id=skill_id,
                skill_name=(
                    skill_names[
                        skill_id
                    ]
                ),
                career_count=career_count,
                career_share=career_share,
            )
        )

    competency_frequencies.sort(
        key=lambda item: (
            -item.career_count,
            item.skill_name.casefold(),
            item.skill_id,
        )
    )

    saturation_diagnostics = []

    for target_career in careers:
        target_skill_set = (
            career_skill_sets[
                target_career.id
            ]
        )

        if not target_skill_set:
            saturation_diagnostics.append(
                CareerSaturationDiagnostic(
                    career_id=(
                        target_career.id
                    ),
                    career_name=(
                        target_career.name
                    ),
                    competency_count=0,
                    target_rank=None,
                    target_score=None,
                    perfect_score_count=0,
                    perfect_score_careers=(),
                    subset_career_count=0,
                    subset_careers=(),
                )
            )

            continue

        ranked_results = (
            _score_skill_set(
                student_skill_ids=tuple(
                    sorted(
                        target_skill_set
                    )
                ),
                careers=careers,
                competencies_by_career=(
                    competencies_by_career
                ),
            )
        )

        target_result = next(
            result
            for result in ranked_results
            if result.career_id
            == target_career.id
        )

        perfect_results = tuple(
            result
            for result in ranked_results
            if (
                result.recommendation_score
                == Decimal("100.00")
            )
        )

        subset_careers = []

        for candidate_career in careers:
            candidate_skill_set = (
                career_skill_sets[
                    candidate_career.id
                ]
            )

            if (
                not candidate_skill_set
                or candidate_career.id
                == target_career.id
            ):
                continue

            if candidate_skill_set.issubset(
                target_skill_set
            ):
                subset_careers.append(
                    candidate_career.name
                )

        subset_careers.sort(
            key=str.casefold
        )

        saturation_diagnostics.append(
            CareerSaturationDiagnostic(
                career_id=(
                    target_career.id
                ),
                career_name=(
                    target_career.name
                ),
                competency_count=(
                    len(target_skill_set)
                ),
                target_rank=(
                    target_result.rank
                ),
                target_score=(
                    target_result
                    .recommendation_score
                ),
                perfect_score_count=(
                    len(perfect_results)
                ),
                perfect_score_careers=tuple(
                    result.career_name
                    for result
                    in perfect_results
                ),
                subset_career_count=(
                    len(subset_careers)
                ),
                subset_careers=tuple(
                    subset_careers
                ),
            )
        )

    return V1DiagnosticReport(
        active_career_count=(
            active_career_count
        ),
        career_count_with_evidence=(
            active_career_count
            - len(
                careers_without_evidence
            )
        ),
        career_count_without_evidence=(
            len(
                careers_without_evidence
            )
        ),
        careers_without_evidence=tuple(
            careers_without_evidence
        ),
        competency_frequencies=tuple(
            competency_frequencies
        ),
        saturation_diagnostics=tuple(
            saturation_diagnostics
        ),
    )