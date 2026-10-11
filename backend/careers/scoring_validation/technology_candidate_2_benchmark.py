"""
Benchmark runner for GradNavi Technology Candidate T2.

Technology Candidate T2 measures Student-centred alignment with
occupation-specific technologies marked In Demand by O*NET.

The benchmark uses the same synthetic profiles as Technology
Candidate T1 so the two models receive identical inputs.

The benchmark evaluates:

1. Exact GradNavi Career ranking.
2. O*NET occupation-group ranking.
3. Technology evidence coverage.

Only Careers with usable In-Demand technology evidence contribute
to ranking metrics.

Careers without such evidence are reported separately.

No production scoring behaviour or database records are modified.
"""

from dataclasses import dataclass
from decimal import Decimal

from careers.models import Career

from careers.scoring_validation.metrics import (
    RankingMetrics,
    calculate_ranking_metrics,
)

from careers.scoring_validation.occupation_groups import (
    build_career_to_group_map,
    find_group_rank,
)

from careers.scoring_validation.technology_candidate_1 import (
    TechnologyRequirement,
    load_in_demand_technologies_by_career,
)

from careers.scoring_validation.technology_candidate_2 import (
    TechnologyCandidate2Result,
    build_technology_idf_weights,
    calculate_student_technology_signal,
    calculate_technology_candidate_2_fit,
    rank_technology_candidate_2_results,
)

from careers.scoring_validation.technology_synthetic_profiles import (
    TechnologyBenchmarkCoverage,
    TechnologyBenchmarkScenario,
    TechnologySyntheticBenchmarkProfile,
    build_technology_benchmark_dataset,
)


@dataclass(frozen=True)
class TechnologyCandidate2CaseResult:
    """
    One Technology Candidate T2 benchmark case.
    """

    target_career_id: int
    target_career_name: str

    scenario: TechnologyBenchmarkScenario

    exact_rank: int | None
    occupation_group_rank: int | None

    target_score: Decimal | None

    profile_skill_count: int
    target_requirement_count: int


@dataclass(frozen=True)
class TechnologyCandidate2ScenarioResult:
    """
    Aggregate Technology T2 metrics for one scenario.
    """

    scenario: TechnologyBenchmarkScenario

    case_count: int

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class TechnologyCandidate2BenchmarkReport:
    """
    Complete Technology Candidate T2 benchmark report.
    """

    model_name: str

    coverage: TechnologyBenchmarkCoverage

    case_results: tuple[
        TechnologyCandidate2CaseResult,
        ...
    ]

    scenario_results: tuple[
        TechnologyCandidate2ScenarioResult,
        ...
    ]

    overall_exact_metrics: RankingMetrics

    overall_occupation_group_metrics: RankingMetrics


def score_profile(
    *,
    profile: TechnologySyntheticBenchmarkProfile,
    careers: tuple[
        Career,
        ...
    ],
    requirements_by_career: dict[
        int,
        tuple[
            TechnologyRequirement,
            ...
        ],
    ],
    idf_weights: dict,
) -> tuple[
    TechnologyCandidate2Result,
    ...
]:
    """
    Score one synthetic technology profile using Candidate T2.
    """

    student_signal = (
        calculate_student_technology_signal(
            student_proficiencies=(
                profile.student_proficiencies
            ),
            idf_weights=(
                idf_weights
            ),
        )
    )

    results = []

    for career in careers:
        result = (
            calculate_technology_candidate_2_fit(
                career_id=career.id,
                career_name=career.name,
                student_proficiencies=(
                    profile.student_proficiencies
                ),
                requirements=(
                    requirements_by_career.get(
                        career.id,
                        (),
                    )
                ),
                idf_weights=(
                    idf_weights
                ),
                student_signal=(
                    student_signal
                ),
            )
        )

        results.append(
            result
        )

    return (
        rank_technology_candidate_2_results(
            results
        )
    )


def evaluate_profile(
    *,
    profile: TechnologySyntheticBenchmarkProfile,
    ranked_results: tuple[
        TechnologyCandidate2Result,
        ...
    ],
    career_to_group: dict,
) -> TechnologyCandidate2CaseResult:
    """
    Extract exact-Career and O*NET occupation-group rank.
    """

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

    if target_result is None:
        raise ValueError(
            "Target Career was missing from Technology T2 "
            "results: "
            f"{profile.target_career_name}"
        )

    if target_result.rank is None:
        raise ValueError(
            "A benchmark profile was created for a Career "
            "without scorable Technology T2 evidence: "
            f"{profile.target_career_name}"
        )

    ranked_career_ids = tuple(
        result.career_id
        for result
        in ranked_results
        if result.rank is not None
    )

    group_rank = find_group_rank(
        ranked_career_ids=(
            ranked_career_ids
        ),
        target_career_id=(
            profile.target_career_id
        ),
        career_to_group=(
            career_to_group
        ),
    )

    return TechnologyCandidate2CaseResult(
        target_career_id=(
            profile.target_career_id
        ),
        target_career_name=(
            profile.target_career_name
        ),
        scenario=(
            profile.scenario
        ),
        exact_rank=(
            target_result.rank
        ),
        occupation_group_rank=(
            group_rank
        ),
        target_score=(
            target_result
            .technology_alignment_score
        ),
        profile_skill_count=(
            len(
                profile.skills
            )
        ),
        target_requirement_count=(
            profile.target_requirement_count
        ),
    )


def run_technology_candidate_2_benchmark(
) -> TechnologyCandidate2BenchmarkReport:
    """
    Run Technology Candidate T2 over the same evidence-supported
    benchmark cases used by Technology Candidate T1.
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
            "active",
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

    requirements_by_career = (
        load_in_demand_technologies_by_career(
            career_ids=career_ids
        )
    )

    benchmark_dataset = (
        build_technology_benchmark_dataset(
            careers=careers,
            requirements_by_career=(
                requirements_by_career
            ),
        )
    )

    if not benchmark_dataset.profiles:
        raise ValueError(
            "No evidence-supported Technology benchmark "
            "profiles were generated."
        )

    idf_weights = (
        build_technology_idf_weights(
            requirements_by_career=(
                requirements_by_career
            )
        )
    )

    if not idf_weights:
        raise ValueError(
            "No Technology IDF weights were generated."
        )

    career_to_group = (
        build_career_to_group_map()
    )

    case_results = []

    for profile in benchmark_dataset.profiles:
        ranked_results = score_profile(
            profile=profile,
            careers=careers,
            requirements_by_career=(
                requirements_by_career
            ),
            idf_weights=(
                idf_weights
            ),
        )

        case_results.append(
            evaluate_profile(
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

    for scenario in TechnologyBenchmarkScenario:
        scenario_cases = tuple(
            result
            for result
            in case_results_tuple
            if result.scenario
            == scenario
        )

        if not scenario_cases:
            continue

        exact_metrics = (
            calculate_ranking_metrics(
                result.exact_rank
                for result
                in scenario_cases
            )
        )

        occupation_group_metrics = (
            calculate_ranking_metrics(
                result.occupation_group_rank
                for result
                in scenario_cases
            )
        )

        scenario_results.append(
            TechnologyCandidate2ScenarioResult(
                scenario=scenario,
                case_count=(
                    len(
                        scenario_cases
                    )
                ),
                exact_metrics=(
                    exact_metrics
                ),
                occupation_group_metrics=(
                    occupation_group_metrics
                ),
            )
        )

    overall_exact_metrics = (
        calculate_ranking_metrics(
            result.exact_rank
            for result
            in case_results_tuple
        )
    )

    overall_occupation_group_metrics = (
        calculate_ranking_metrics(
            result.occupation_group_rank
            for result
            in case_results_tuple
        )
    )

    return TechnologyCandidate2BenchmarkReport(
        model_name=(
            "Technology Candidate T2 - "
            "IDF Student Alignment"
        ),
        coverage=(
            benchmark_dataset.coverage
        ),
        case_results=(
            case_results_tuple
        ),
        scenario_results=tuple(
            scenario_results
        ),
        overall_exact_metrics=(
            overall_exact_metrics
        ),
        overall_occupation_group_metrics=(
            overall_occupation_group_metrics
        ),
    )
