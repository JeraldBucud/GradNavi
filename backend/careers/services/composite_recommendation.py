"""
Production composite Career Recommendation service for GradNavi.

Locked WBS 5.3 composite design:

Competency Fit
    20%

Technology Fit
    20%

AI Semantic Alignment
    60%

Component scores are min-max normalized within one Student
recommendation run before weighted combination.

Technology Fit contributes to one Career only when:

    student_alignment_ratio >= 0.10

If a component is unavailable for one Career, its weight is
redistributed across the available components.

Missing evidence is never converted into a fabricated zero score.

This service composes the existing production WBS 5.3 services.
It does not change their internal formulas.

Database access is read-only.
The embedding provider stays provider-independent.
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

from ai_services.providers.embeddings import (
    EmbeddingProvider,
)

from careers.models import Career

from careers.services.ai_semantic_alignment import (
    SemanticAlignmentContextMode,
    SemanticAlignmentResult,
    score_ai_semantic_alignment,
)

from careers.services.recommendation_scoring import (
    RecommendationResult,
    ScoreStatus,
    generate_recommendations,
)

from careers.services.technology_fit import (
    TechnologyFitResult,
    score_technology_fit,
)

from profiles.models import StudentProfile


COMPETENCY_WEIGHT = Decimal("0.20")

TECHNOLOGY_WEIGHT = Decimal("0.20")

SEMANTIC_WEIGHT = Decimal("0.60")


TECHNOLOGY_ALIGNMENT_THRESHOLD = (
    Decimal("0.10")
)


SCORE_MINIMUM = Decimal("0")

SCORE_MAXIMUM = Decimal("100")

SCORE_QUANTUM = Decimal("0.01")

NORMALIZED_QUANTUM = Decimal(
    "0.000001"
)


@dataclass(frozen=True)
class EffectiveCompositeWeights:
    """
    Effective weights after unavailable components
    are removed and remaining weights are redistributed.
    """

    competency: Decimal

    technology: Decimal

    semantic: Decimal


@dataclass(frozen=True)
class CompositeRecommendationResult:
    """
    Final WBS 5.3 composite result for one Career.
    """

    career_id: int

    career_name: str

    recommendation_score: Decimal


    competency_score: Decimal | None

    competency_normalized_score: (
        Decimal | None
    )

    competency_status: ScoreStatus


    technology_score: Decimal | None

    technology_normalized_score: (
        Decimal | None
    )

    technology_status: ScoreStatus

    technology_student_alignment_ratio: (
        Decimal | None
    )

    technology_active: bool


    semantic_alignment_score: Decimal

    semantic_normalized_score: Decimal

    semantic_context_mode: (
        SemanticAlignmentContextMode
    )


    effective_competency_weight: Decimal

    effective_technology_weight: Decimal

    effective_semantic_weight: Decimal


    competency_result: RecommendationResult

    technology_result: TechnologyFitResult

    semantic_result: SemanticAlignmentResult


    rank: int | None = None


@dataclass(frozen=True)
class CompositeRecommendationReport:
    """
    One complete production composite recommendation run.
    """

    model: str | None

    prompt_tokens: int

    total_tokens: int

    career_count: int

    results: tuple[
        CompositeRecommendationResult,
        ...
    ]


def min_max_normalize_scores(
    scores: Mapping[
        int,
        Decimal | None,
    ],
) -> dict[
    int,
    Decimal | None,
]:
    """
    Normalize one component across one Student run.

    Available component scores map onto 0 to 100.

    Missing values stay None.

    If every available score is equal, the component
    has no ranking discrimination and all available
    normalized values become zero.
    """

    available = [
        value
        for value
        in scores.values()
        if value is not None
    ]

    if not available:
        return {
            career_id: None
            for career_id
            in scores
        }

    for value in available:
        if not (
            SCORE_MINIMUM
            <= value
            <= SCORE_MAXIMUM
        ):
            raise ValueError(
                "Component score must stay "
                "within 0 to 100."
            )

    minimum = min(
        available
    )

    maximum = max(
        available
    )

    if maximum == minimum:
        return {
            career_id: (
                Decimal("0")
                if value is not None
                else None
            )
            for (
                career_id,
                value,
            )
            in scores.items()
        }

    span = (
        maximum
        - minimum
    )

    normalized = {}

    for (
        career_id,
        value,
    ) in scores.items():
        if value is None:
            normalized[
                career_id
            ] = None

            continue

        normalized[
            career_id
        ] = (
            (
                (
                    value
                    - minimum
                )
                / span
                * SCORE_MAXIMUM
            )
            .quantize(
                NORMALIZED_QUANTUM,
                rounding=ROUND_HALF_UP,
            )
        )

    return normalized


def technology_component_is_active(
    result: TechnologyFitResult,
) -> bool:
    """
    Apply the locked Technology Fit activation rule.
    """

    if (
        result.score_status
        != ScoreStatus.SCORED
    ):
        return False

    if (
        result.technology_fit_score
        is None
    ):
        return False

    if (
        result.student_alignment_ratio
        is None
    ):
        return False

    return (
        result.student_alignment_ratio
        >= TECHNOLOGY_ALIGNMENT_THRESHOLD
    )


def calculate_effective_weights(
    *,
    competency_available: bool,
    technology_available: bool,
    semantic_available: bool,
) -> EffectiveCompositeWeights:
    """
    Redistribute unavailable component weight.

    Original weights:

        Competency 20%
        Technology 20%
        Semantic   60%
    """

    competency_weight = (
        COMPETENCY_WEIGHT
        if competency_available
        else Decimal("0")
    )

    technology_weight = (
        TECHNOLOGY_WEIGHT
        if technology_available
        else Decimal("0")
    )

    semantic_weight = (
        SEMANTIC_WEIGHT
        if semantic_available
        else Decimal("0")
    )

    total = (
        competency_weight
        + technology_weight
        + semantic_weight
    )

    if total <= Decimal("0"):
        raise ValueError(
            "Composite recommendation requires "
            "at least one available component."
        )

    return EffectiveCompositeWeights(
        competency=(
            competency_weight
            / total
        ),
        technology=(
            technology_weight
            / total
        ),
        semantic=(
            semantic_weight
            / total
        ),
    )


def calculate_composite_score(
    *,
    competency_normalized: Decimal | None,
    technology_normalized: Decimal | None,
    semantic_normalized: Decimal | None,
    technology_active: bool,
) -> tuple[
    Decimal,
    EffectiveCompositeWeights,
]:
    """
    Calculate one normalized weighted composite score.
    """

    competency_available = (
        competency_normalized
        is not None
    )

    technology_available = (
        technology_normalized
        is not None
        and technology_active
    )

    semantic_available = (
        semantic_normalized
        is not None
    )

    weights = (
        calculate_effective_weights(
            competency_available=(
                competency_available
            ),
            technology_available=(
                technology_available
            ),
            semantic_available=(
                semantic_available
            ),
        )
    )

    score = Decimal("0")

    if competency_available:
        score += (
            competency_normalized
            * weights.competency
        )

    if technology_available:
        score += (
            technology_normalized
            * weights.technology
        )

    if semantic_available:
        score += (
            semantic_normalized
            * weights.semantic
        )

    score = score.quantize(
        SCORE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )

    score = max(
        SCORE_MINIMUM,
        min(
            SCORE_MAXIMUM,
            score,
        ),
    )

    return (
        score,
        weights,
    )


def _validate_component_identity(
    *,
    competency_results: Iterable[
        RecommendationResult
    ],
    technology_results: Iterable[
        TechnologyFitResult
    ],
    semantic_results: Iterable[
        SemanticAlignmentResult
    ],
) -> tuple[
    tuple[
        RecommendationResult,
        ...
    ],
    tuple[
        TechnologyFitResult,
        ...
    ],
    tuple[
        SemanticAlignmentResult,
        ...
    ],
]:
    """
    Confirm all component services scored the same Careers.
    """

    competency = tuple(
        competency_results
    )

    technology = tuple(
        technology_results
    )

    semantic = tuple(
        semantic_results
    )

    if (
        not competency
        and not technology
        and not semantic
    ):
        return (
            (),
            (),
            (),
        )

    competency_ids = {
        result.career_id
        for result
        in competency
    }

    technology_ids = {
        result.career_id
        for result
        in technology
    }

    semantic_ids = {
        result.career_id
        for result
        in semantic
    }

    if not (
        competency_ids
        == technology_ids
        == semantic_ids
    ):
        raise ValueError(
            "Composite component Career sets "
            "must match exactly."
        )

    competency_names = {
        result.career_id: (
            result.career_name
        )
        for result
        in competency
    }

    technology_names = {
        result.career_id: (
            result.career_name
        )
        for result
        in technology
    }

    semantic_names = {
        result.career_id: (
            result.career_name
        )
        for result
        in semantic
    }

    for career_id in competency_ids:
        names = {
            competency_names[
                career_id
            ],
            technology_names[
                career_id
            ],
            semantic_names[
                career_id
            ],
        }

        if len(names) != 1:
            raise ValueError(
                "Composite component Career names "
                "must match."
            )

    return (
        competency,
        technology,
        semantic,
    )


def rank_composite_results(
    results: Iterable[
        CompositeRecommendationResult
    ],
) -> tuple[
    CompositeRecommendationResult,
    ...
]:
    """
    Rank final composite recommendations.

    Rules:

    1. Higher final recommendation score.
    2. Career name alphabetically.
    3. Career ID ascending.
    """

    ordered = list(
        results
    )

    ordered.sort(
        key=lambda result: (
            -result.recommendation_score,
            result.career_name.casefold(),
            result.career_id,
        )
    )

    return tuple(
        replace(
            result,
            rank=rank,
        )
        for (
            rank,
            result,
        )
        in enumerate(
            ordered,
            start=1,
        )
    )


def build_composite_results(
    *,
    competency_results: Iterable[
        RecommendationResult
    ],
    technology_results: Iterable[
        TechnologyFitResult
    ],
    semantic_results: Iterable[
        SemanticAlignmentResult
    ],
) -> tuple[
    CompositeRecommendationResult,
    ...
]:
    """
    Combine already-calculated production component results.
    """

    (
        competency,
        technology,
        semantic,
    ) = _validate_component_identity(
        competency_results=(
            competency_results
        ),
        technology_results=(
            technology_results
        ),
        semantic_results=(
            semantic_results
        ),
    )

    if not semantic:
        return ()

    competency_by_id = {
        result.career_id: result
        for result
        in competency
    }

    technology_by_id = {
        result.career_id: result
        for result
        in technology
    }

    semantic_by_id = {
        result.career_id: result
        for result
        in semantic
    }

    competency_raw = {
        result.career_id: (
            result.recommendation_score
            if (
                result.score_status
                == ScoreStatus.SCORED
            )
            else None
        )
        for result
        in competency
    }

    technology_raw = {
        result.career_id: (
            result.technology_fit_score
            if (
                result.score_status
                == ScoreStatus.SCORED
            )
            else None
        )
        for result
        in technology
    }

    semantic_raw = {
        result.career_id: (
            result.semantic_alignment_score
        )
        for result
        in semantic
    }

    competency_normalized = (
        min_max_normalize_scores(
            competency_raw
        )
    )

    technology_normalized = (
        min_max_normalize_scores(
            technology_raw
        )
    )

    semantic_normalized = (
        min_max_normalize_scores(
            semantic_raw
        )
    )

    results = []

    for semantic_result in semantic:
        career_id = (
            semantic_result.career_id
        )

        competency_result = (
            competency_by_id[
                career_id
            ]
        )

        technology_result = (
            technology_by_id[
                career_id
            ]
        )

        technology_active = (
            technology_component_is_active(
                technology_result
            )
        )

        (
            recommendation_score,
            effective_weights,
        ) = calculate_composite_score(
            competency_normalized=(
                competency_normalized[
                    career_id
                ]
            ),
            technology_normalized=(
                technology_normalized[
                    career_id
                ]
            ),
            semantic_normalized=(
                semantic_normalized[
                    career_id
                ]
            ),
            technology_active=(
                technology_active
            ),
        )

        results.append(
            CompositeRecommendationResult(
                career_id=career_id,
                career_name=(
                    semantic_result
                    .career_name
                ),
                recommendation_score=(
                    recommendation_score
                ),
                competency_score=(
                    competency_raw[
                        career_id
                    ]
                ),
                competency_normalized_score=(
                    competency_normalized[
                        career_id
                    ]
                ),
                competency_status=(
                    competency_result
                    .score_status
                ),
                technology_score=(
                    technology_raw[
                        career_id
                    ]
                ),
                technology_normalized_score=(
                    technology_normalized[
                        career_id
                    ]
                ),
                technology_status=(
                    technology_result
                    .score_status
                ),
                technology_student_alignment_ratio=(
                    technology_result
                    .student_alignment_ratio
                ),
                technology_active=(
                    technology_active
                ),
                semantic_alignment_score=(
                    semantic_result
                    .semantic_alignment_score
                ),
                semantic_normalized_score=(
                    semantic_normalized[
                        career_id
                    ]
                ),
                semantic_context_mode=(
                    semantic_result
                    .context_mode
                ),
                effective_competency_weight=(
                    effective_weights
                    .competency
                ),
                effective_technology_weight=(
                    effective_weights
                    .technology
                ),
                effective_semantic_weight=(
                    effective_weights
                    .semantic
                ),
                competency_result=(
                    competency_result
                ),
                technology_result=(
                    technology_result
                ),
                semantic_result=(
                    semantic_result
                ),
            )
        )

    return rank_composite_results(
        results
    )


def generate_composite_recommendations(
    *,
    student_profile_id: int,
    embedding_provider: EmbeddingProvider,
) -> CompositeRecommendationReport:
    """
    Run the complete production WBS 5.3 scoring stack.

    Components:

    - Competency Fit
    - Technology Fit
    - AI Semantic Alignment
    - Normalization
    - Technology activation
    - Composite weighting
    - Final ranking

    Database access is read-only.
    """

    if student_profile_id <= 0:
        raise ValueError(
            "student_profile_id must be "
            "greater than zero."
        )

    student_profile = (
        StudentProfile.objects
        .select_related(
            "user"
        )
        .get(
            id=student_profile_id
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
    )

    if not careers:
        return CompositeRecommendationReport(
            model=None,
            prompt_tokens=0,
            total_tokens=0,
            career_count=0,
            results=(),
        )

    competency_results = (
        generate_recommendations(
            student_profile_id=(
                student_profile_id
            )
        )
    )

    technology_results = (
        score_technology_fit(
            student_profile_id=(
                student_profile_id
            )
        )
    )

    semantic_report = (
        score_ai_semantic_alignment(
            student_profile=(
                student_profile
            ),
            careers=careers,
            embedding_provider=(
                embedding_provider
            ),
        )
    )

    results = (
        build_composite_results(
            competency_results=(
                competency_results
            ),
            technology_results=(
                technology_results
            ),
            semantic_results=(
                semantic_report.results
            ),
        )
    )

    return CompositeRecommendationReport(
        model=semantic_report.model,
        prompt_tokens=(
            semantic_report
            .prompt_tokens
        ),
        total_tokens=(
            semantic_report
            .total_tokens
        ),
        career_count=len(
            results
        ),
        results=results,
    )
