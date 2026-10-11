"""
Benchmark runner for GradNavi AI Candidate A2.

The benchmark compares three semantic Career representations:

A2-I
    Career identity only.

A2-IE
    Career identity plus essential ESCO skills.

A2-IT
    Career identity plus In-Demand technologies.

All synthetic Student profiles are evidence-derived and exclude
target Career metadata.

The benchmark embeds every unique Student and Career context once,
then performs all ranking calculations locally.

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
from typing import Iterable

from ai_services.providers.embeddings import (
    EmbeddingProvider,
)

from careers.models import Career

from careers.scoring_validation.ai_candidate_1 import (
    calculate_cosine_similarity,
)

from careers.scoring_validation.ai_candidate_2_contexts import (
    AISemanticCandidate,
    A2CareerContext,
    build_all_a2_contexts,
)

from careers.scoring_validation.ai_candidate_2_synthetic_profiles import (
    AISemanticBenchmarkScenario,
    AISemanticSyntheticProfile,
    build_a2_benchmark_dataset,
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
class A2RankedCareer:
    """
    One ranked Career for one synthetic Student profile.
    """

    career_id: int
    career_name: str

    similarity: Decimal

    rank: int


@dataclass(frozen=True)
class A2BenchmarkCaseResult:
    """
    One benchmark result for one Candidate and one profile.
    """

    candidate: AISemanticCandidate

    target_career_id: int
    target_career_name: str

    scenario: AISemanticBenchmarkScenario

    exact_rank: int | None
    occupation_group_rank: int | None

    target_similarity: Decimal | None

    numerical_competency_count: int
    essential_esco_count: int
    technology_count: int


@dataclass(frozen=True)
class A2CandidateScenarioResult:
    """
    Aggregate metrics for one Candidate and scenario.
    """

    candidate: AISemanticCandidate

    scenario: AISemanticBenchmarkScenario

    case_count: int

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class A2CandidateResult:
    """
    Overall metrics for one A2 Candidate.
    """

    candidate: AISemanticCandidate

    case_count: int

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class A2BenchmarkReport:
    """
    Complete A2 benchmark result.
    """

    model: str

    prompt_tokens: int
    total_tokens: int

    unique_text_count: int

    active_career_count: int
    profile_count: int
    evaluated_case_count: int

    case_results: tuple[
        A2BenchmarkCaseResult,
        ...
    ]

    scenario_results: tuple[
        A2CandidateScenarioResult,
        ...
    ]

    candidate_results: tuple[
        A2CandidateResult,
        ...
    ]


def build_unique_text_plan(
    texts: Iterable[str],
) -> tuple[
    tuple[str, ...],
    dict[str, int],
]:
    """
    Deduplicate embedding text while preserving first-seen order.
    """

    unique_texts = []
    text_to_index = {}

    for text in texts:
        normalized = text.strip()

        if not normalized:
            raise ValueError(
                "A2 benchmark embedding text "
                "must not be blank."
            )

        if normalized in text_to_index:
            continue

        text_to_index[
            normalized
        ] = len(
            unique_texts
        )

        unique_texts.append(
            normalized
        )

    return (
        tuple(
            unique_texts
        ),
        text_to_index,
    )


def rank_candidate_for_profile(
    *,
    profile_vector,
    careers: tuple[
        Career,
        ...,
    ],
    contexts_by_career_id: dict[
        int,
        A2CareerContext,
    ],
    vectors_by_text: dict[
        str,
        tuple[float, ...],
    ],
) -> tuple[
    A2RankedCareer,
    ...,
]:
    """
    Rank all Careers against one synthetic Student vector.
    """

    ranked = []

    for career in careers:
        context = (
            contexts_by_career_id[
                career.id
            ]
        )

        career_vector = (
            vectors_by_text[
                context.text.strip()
            ]
        )

        similarity = (
            calculate_cosine_similarity(
                first=profile_vector,
                second=career_vector,
            )
        )

        ranked.append(
            (
                career,
                similarity,
            )
        )

    ranked.sort(
        key=lambda item: (
            -item[1],
            item[0].name.casefold(),
            item[0].id,
        )
    )

    return tuple(
        A2RankedCareer(
            career_id=career.id,
            career_name=career.name,
            similarity=similarity,
            rank=rank,
        )
        for rank, (
            career,
            similarity,
        )
        in enumerate(
            ranked,
            start=1,
        )
    )


def evaluate_case(
    *,
    candidate: AISemanticCandidate,
    profile: AISemanticSyntheticProfile,
    ranked_results: tuple[
        A2RankedCareer,
        ...,
    ],
    career_to_group: dict,
) -> A2BenchmarkCaseResult:
    """
    Evaluate one ranked A2 result.
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

    return A2BenchmarkCaseResult(
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
        target_similarity=(
            target_result.similarity
            if target_result
            else None
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


def build_candidate_context_maps(
    *,
    careers: tuple[
        Career,
        ...,
    ],
) -> dict[
    AISemanticCandidate,
    dict[
        int,
        A2CareerContext,
    ],
]:
    """
    Build all A2 Career contexts.
    """

    result = {
        candidate: {}
        for candidate
        in AISemanticCandidate
    }

    for career in careers:
        contexts = (
            build_all_a2_contexts(
                career=career
            )
        )

        for context in contexts:
            result[
                context.candidate
            ][
                career.id
            ] = context

    return result


def run_ai_candidate_2_benchmark(
    *,
    embedding_provider: EmbeddingProvider,
) -> A2BenchmarkReport:
    """
    Run all A2 Candidates over all synthetic benchmark profiles.
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

    benchmark_dataset = (
        build_a2_benchmark_dataset()
    )

    if not benchmark_dataset.profiles:
        raise ValueError(
            "No A2 benchmark profiles "
            "were generated."
        )

    contexts = (
        build_candidate_context_maps(
            careers=careers
        )
    )

    texts = []

    for profile in (
        benchmark_dataset.profiles
    ):
        texts.append(
            profile.text
        )

    for candidate in AISemanticCandidate:
        for career in careers:
            texts.append(
                contexts[
                    candidate
                ][
                    career.id
                ].text
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
            "match A2 benchmark text count."
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

    for profile in (
        benchmark_dataset.profiles
    ):
        profile_vector = (
            vectors_by_text[
                profile.text.strip()
            ]
        )

        for candidate in (
            AISemanticCandidate
        ):
            ranked_results = (
                rank_candidate_for_profile(
                    profile_vector=(
                        profile_vector
                    ),
                    careers=careers,
                    contexts_by_career_id=(
                        contexts[
                            candidate
                        ]
                    ),
                    vectors_by_text=(
                        vectors_by_text
                    ),
                )
            )

            case_results.append(
                evaluate_case(
                    candidate=candidate,
                    profile=profile,
                    ranked_results=(
                        ranked_results
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
        AISemanticCandidate
    ):
        for scenario in (
            AISemanticBenchmarkScenario
        ):
            selected_cases = tuple(
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

            if not selected_cases:
                continue

            scenario_results.append(
                A2CandidateScenarioResult(
                    candidate=candidate,
                    scenario=scenario,
                    case_count=len(
                        selected_cases
                    ),
                    exact_metrics=(
                        calculate_ranking_metrics(
                            result.exact_rank
                            for result
                            in selected_cases
                        )
                    ),
                    occupation_group_metrics=(
                        calculate_ranking_metrics(
                            result
                            .occupation_group_rank
                            for result
                            in selected_cases
                        )
                    ),
                )
            )

    candidate_results = []

    for candidate in (
        AISemanticCandidate
    ):
        selected_cases = tuple(
            result
            for result
            in case_results_tuple
            if (
                result.candidate
                == candidate
            )
        )

        candidate_results.append(
            A2CandidateResult(
                candidate=candidate,
                case_count=len(
                    selected_cases
                ),
                exact_metrics=(
                    calculate_ranking_metrics(
                        result.exact_rank
                        for result
                        in selected_cases
                    )
                ),
                occupation_group_metrics=(
                    calculate_ranking_metrics(
                        result.occupation_group_rank
                        for result
                        in selected_cases
                    )
                ),
            )
        )

    return A2BenchmarkReport(
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
            benchmark_dataset.profiles
        ),
        evaluated_case_count=len(
            case_results_tuple
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
