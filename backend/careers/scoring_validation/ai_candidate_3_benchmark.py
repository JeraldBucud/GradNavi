"""
Benchmark runner for GradNavi AI Candidate A3.

A3 keeps AI Semantic Alignment separate from Technology Fit.

A3 compares four fixed combinations of:

1. Career Identity semantic similarity.
2. Essential ESCO semantic similarity.

Candidates:

A3-90
    90% Identity
    10% Essential ESCO

A3-80
    80% Identity
    20% Essential ESCO

A3-70
    70% Identity
    30% Essential ESCO

A3-60
    60% Identity
    40% Essential ESCO

If a Career has no approved essential ESCO evidence,
the Career Identity similarity receives the full weight.

Technology evidence is not part of the A3 Career semantic score.

The same 72 evidence-derived synthetic profiles from A2 are reused.

Metrics:

- Hit@1
- Hit@3
- Hit@5
- Mean Reciprocal Rank
- NDCG@5
- O*NET occupation-group ranking

This is structural validation against GradNavi reference data.
It is not independent external validation.
"""

from dataclasses import dataclass
from decimal import Decimal

from ai_services.providers.embeddings import (
    EmbeddingProvider,
)

from careers.models import Career

from careers.scoring_validation.ai_candidate_1 import (
    calculate_cosine_similarity,
)

from careers.scoring_validation.ai_candidate_2_benchmark import (
    build_unique_text_plan,
)

from careers.scoring_validation.ai_candidate_2_synthetic_profiles import (
    AISemanticBenchmarkScenario,
    AISemanticSyntheticProfile,
    build_a2_benchmark_dataset,
)

from careers.scoring_validation.ai_candidate_3 import (
    A3CareerContexts,
    A3CareerResult,
    A3WeightingCandidate,
    build_a3_career_contexts,
    build_a3_result,
    rank_a3_results,
)

from careers.scoring_validation.metrics import (
    RankingMetrics,
    calculate_ranking_metrics,
    find_target_rank,
)

from careers.scoring_validation.occupation_groups import (
    build_career_to_group_map,
    find_group_rank,
)


@dataclass(frozen=True)
class A3BenchmarkCaseResult:
    """
    One A3 benchmark case.
    """

    candidate: A3WeightingCandidate

    target_career_id: int
    target_career_name: str

    scenario: AISemanticBenchmarkScenario

    exact_rank: int | None
    occupation_group_rank: int | None

    target_semantic_score: Decimal | None

    target_identity_similarity: Decimal | None

    target_esco_similarity: Decimal | None

    target_has_esco: bool

    numerical_competency_count: int
    essential_esco_count: int
    technology_count: int


@dataclass(frozen=True)
class A3CandidateScenarioResult:
    """
    Metrics for one A3 Candidate and one scenario.
    """

    candidate: A3WeightingCandidate

    scenario: AISemanticBenchmarkScenario

    case_count: int

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class A3CandidateResult:
    """
    Overall metrics for one A3 weighting Candidate.
    """

    candidate: A3WeightingCandidate

    case_count: int

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class A3BenchmarkReport:
    """
    Complete A3 benchmark report.
    """

    model: str

    prompt_tokens: int
    total_tokens: int

    unique_text_count: int

    active_career_count: int
    profile_count: int
    evaluated_case_count: int

    career_with_esco_count: int
    career_without_esco_count: int

    case_results: tuple[
        A3BenchmarkCaseResult,
        ...
    ]

    scenario_results: tuple[
        A3CandidateScenarioResult,
        ...
    ]

    candidate_results: tuple[
        A3CandidateResult,
        ...
    ]


def build_a3_context_map(
    *,
    careers: tuple[
        Career,
        ...,
    ],
) -> dict[
    int,
    A3CareerContexts,
]:
    """
    Build the A3 contexts for every active Career.
    """

    contexts = {}

    for career in careers:
        context = build_a3_career_contexts(
            career=career
        )

        contexts[
            career.id
        ] = context

    return contexts


def rank_a3_profile(
    *,
    profile_vector,
    careers: tuple,
    contexts_by_career_id: dict[
        int,
        A3CareerContexts,
    ],
    vectors_by_text: dict[
        str,
        tuple[float, ...],
    ],
    candidate: A3WeightingCandidate,
) -> tuple[
    A3CareerResult,
    ...,
]:
    """
    Rank all Careers for one synthetic Student profile.
    """

    results = []

    for career in careers:
        context = (
            contexts_by_career_id[
                career.id
            ]
        )

        identity_vector = (
            vectors_by_text[
                context.identity_text.strip()
            ]
        )

        identity_similarity = (
            calculate_cosine_similarity(
                first=profile_vector,
                second=identity_vector,
            )
        )

        esco_similarity = None

        if (
            context.essential_esco_text
            is not None
        ):
            esco_vector = (
                vectors_by_text[
                    context
                    .essential_esco_text
                    .strip()
                ]
            )

            esco_similarity = (
                calculate_cosine_similarity(
                    first=profile_vector,
                    second=esco_vector,
                )
            )

        results.append(
            build_a3_result(
                career_id=career.id,
                career_name=career.name,
                candidate=candidate,
                identity_similarity=(
                    identity_similarity
                ),
                esco_similarity=(
                    esco_similarity
                ),
            )
        )

    return rank_a3_results(
        results
    )


def evaluate_a3_case(
    *,
    candidate: A3WeightingCandidate,
    profile: AISemanticSyntheticProfile,
    ranked_results: tuple[
        A3CareerResult,
        ...,
    ],
    contexts_by_career_id: dict[
        int,
        A3CareerContexts,
    ],
    career_to_group: dict,
) -> A3BenchmarkCaseResult:
    """
    Evaluate one A3 ranked result.
    """

    ranked_ids = tuple(
        result.career_id
        for result
        in ranked_results
    )

    exact_rank = find_target_rank(
        ranked_career_ids=ranked_ids,
        target_career_id=(
            profile.target_career_id
        ),
    )

    group_rank = find_group_rank(
        ranked_career_ids=ranked_ids,
        target_career_id=(
            profile.target_career_id
        ),
        career_to_group=(
            career_to_group
        ),
    )

    target_result = next(
        (
            result
            for result
            in ranked_results
            if (
                result.career_id
                == profile.target_career_id
            )
        ),
        None,
    )

    target_context = (
        contexts_by_career_id[
            profile.target_career_id
        ]
    )

    return A3BenchmarkCaseResult(
        candidate=candidate,
        target_career_id=(
            profile.target_career_id
        ),
        target_career_name=(
            profile.target_career_name
        ),
        scenario=profile.scenario,
        exact_rank=exact_rank,
        occupation_group_rank=(
            group_rank
        ),
        target_semantic_score=(
            target_result
            .semantic_alignment_score
            if target_result
            else None
        ),
        target_identity_similarity=(
            target_result
            .identity_similarity
            if target_result
            else None
        ),
        target_esco_similarity=(
            target_result
            .esco_similarity
            if target_result
            else None
        ),
        target_has_esco=(
            target_context
            .essential_esco_count
            > 0
        ),
        numerical_competency_count=(
            profile
            .numerical_competency_count
        ),
        essential_esco_count=(
            profile
            .essential_esco_count
        ),
        technology_count=(
            profile
            .technology_count
        ),
    )


def run_ai_candidate_3_benchmark(
    *,
    embedding_provider: EmbeddingProvider,
) -> A3BenchmarkReport:
    """
    Run all A3 weighting Candidates.
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

    dataset = (
        build_a2_benchmark_dataset()
    )

    if not dataset.profiles:
        raise ValueError(
            "No A3 benchmark profiles "
            "were generated."
        )

    contexts = (
        build_a3_context_map(
            careers=careers
        )
    )

    texts = []

    for profile in dataset.profiles:
        texts.append(
            profile.text
        )

    for career in careers:
        context = contexts[
            career.id
        ]

        texts.append(
            context.identity_text
        )

        if (
            context.essential_esco_text
            is not None
        ):
            texts.append(
                context.essential_esco_text
            )

    (
        unique_texts,
        text_to_index,
    ) = build_unique_text_plan(
        texts
    )

    embedding_batch = (
        embedding_provider.embed_texts(
            texts=unique_texts
        )
    )

    if (
        embedding_batch.vector_count
        != len(
            unique_texts
        )
    ):
        raise ValueError(
            "Embedding vector count does not "
            "match A3 benchmark text count."
        )

    vectors_by_text = {
        text: (
            embedding_batch.vectors[
                index
            ]
        )
        for text, index
        in text_to_index.items()
    }

    career_to_group = (
        build_career_to_group_map()
    )

    case_results = []

    for profile in dataset.profiles:
        profile_vector = (
            vectors_by_text[
                profile.text.strip()
            ]
        )

        for candidate in (
            A3WeightingCandidate
        ):
            ranked = rank_a3_profile(
                profile_vector=(
                    profile_vector
                ),
                careers=careers,
                contexts_by_career_id=(
                    contexts
                ),
                vectors_by_text=(
                    vectors_by_text
                ),
                candidate=candidate,
            )

            case_results.append(
                evaluate_a3_case(
                    candidate=candidate,
                    profile=profile,
                    ranked_results=ranked,
                    contexts_by_career_id=(
                        contexts
                    ),
                    career_to_group=(
                        career_to_group
                    ),
                )
            )

    case_results_tuple = tuple(
        case_results
    )

    scenario_results = []

    for candidate in (
        A3WeightingCandidate
    ):
        for scenario in (
            AISemanticBenchmarkScenario
        ):
            selected = tuple(
                result
                for result
                in case_results_tuple
                if (
                    result.candidate
                    == candidate
                    and result.scenario
                    == scenario
                )
            )

            if not selected:
                continue

            scenario_results.append(
                A3CandidateScenarioResult(
                    candidate=candidate,
                    scenario=scenario,
                    case_count=len(
                        selected
                    ),
                    exact_metrics=(
                        calculate_ranking_metrics(
                            result.exact_rank
                            for result
                            in selected
                        )
                    ),
                    occupation_group_metrics=(
                        calculate_ranking_metrics(
                            result
                            .occupation_group_rank
                            for result
                            in selected
                        )
                    ),
                )
            )

    candidate_results = []

    for candidate in (
        A3WeightingCandidate
    ):
        selected = tuple(
            result
            for result
            in case_results_tuple
            if (
                result.candidate
                == candidate
            )
        )

        candidate_results.append(
            A3CandidateResult(
                candidate=candidate,
                case_count=len(
                    selected
                ),
                exact_metrics=(
                    calculate_ranking_metrics(
                        result.exact_rank
                        for result
                        in selected
                    )
                ),
                occupation_group_metrics=(
                    calculate_ranking_metrics(
                        result
                        .occupation_group_rank
                        for result
                        in selected
                    )
                ),
            )
        )

    careers_with_esco = sum(
        1
        for context
        in contexts.values()
        if (
            context.essential_esco_count
            > 0
        )
    )

    return A3BenchmarkReport(
        model=embedding_batch.model,
        prompt_tokens=(
            embedding_batch.prompt_tokens
        ),
        total_tokens=(
            embedding_batch.total_tokens
        ),
        unique_text_count=len(
            unique_texts
        ),
        active_career_count=len(
            careers
        ),
        profile_count=len(
            dataset.profiles
        ),
        evaluated_case_count=len(
            case_results_tuple
        ),
        career_with_esco_count=(
            careers_with_esco
        ),
        career_without_esco_count=(
            len(careers)
            - careers_with_esco
        ),
        case_results=(
            case_results_tuple
        ),
        scenario_results=tuple(
            scenario_results
        ),
        candidate_results=tuple(
            candidate_results
        ),
    )
