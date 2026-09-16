"""
Benchmark runner for GradNavi Technology Candidate T3.

Technology Candidate T3 combines:

1. IDF-weighted Student Alignment.
2. O*NET demand-percentage-weighted Career Coverage.
3. Harmonic mean of both signals.

The benchmark reuses the same synthetic profiles used by
Technology Candidates T1 and T2.

Only Careers with usable In-Demand technology evidence contribute
to ranking metrics.

Careers without technology evidence stay visible through benchmark
coverage reporting.

Production recommendation scoring is not modified.
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
    build_technology_idf_weights,
    calculate_student_technology_signal,
)

from careers.scoring_validation.technology_candidate_3 import (
    TechnologyCandidate3Result,
    TechnologyDemandRequirement,
    calculate_technology_candidate_3_fit,
    load_demand_weighted_technologies_by_career,
    rank_technology_candidate_3_results,
)

from careers.scoring_validation.technology_synthetic_profiles import (
    TechnologyBenchmarkCoverage,
    TechnologyBenchmarkScenario,
    TechnologySyntheticBenchmarkProfile,
    build_technology_benchmark_dataset,
)


@dataclass(frozen=True)
class TechnologyCandidate3CaseResult:
    """
    One Technology Candidate T3 benchmark case.
    """

    target_career_id: int
    target_career_name: str

    scenario: TechnologyBenchmarkScenario

    exact_rank: int | None
    occupation_group_rank: int | None

    target_score: Decimal | None

    target_alignment_ratio: Decimal | None
    target_demand_coverage_ratio: Decimal | None

    profile_skill_count: int
    target_requirement_count: int


@dataclass(frozen=True)
class TechnologyCandidate3ScenarioResult:
    """
    Aggregate Technology T3 metrics for one scenario.
    """

    scenario: TechnologyBenchmarkScenario

    case_count: int

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class TechnologyCandidate3BenchmarkReport:
    """
    Complete Technology Candidate T3 benchmark report.
    """

    model_name: str

    coverage: TechnologyBenchmarkCoverage

    case_results: tuple[
        TechnologyCandidate3CaseResult,
        ...
    ]

    scenario_results: tuple[
        TechnologyCandidate3ScenarioResult,
        ...
    ]

    overall_exact_metrics: RankingMetrics

    overall_occupation_group_metrics: RankingMetrics


def validate_requirement_coverage(
    *,
    careers: tuple[
        Career,
        ...
    ],
    t1_requirements_by_career: dict[
        int,
        tuple[
            TechnologyRequirement,
            ...
        ],
    ],
    t3_requirements_by_career: dict[
        int,
        tuple[
            TechnologyDemandRequirement,
            ...
        ],
    ],
):
    """
    Confirm every T1 In-Demand technology used by the benchmark
    has corresponding T3 percentage evidence.
    """

    mismatches = []

    for career in careers:
        t1_requirements = tuple(
            t1_requirements_by_career.get(
                career.id,
                (),
            )
        )

        t3_requirements = tuple(
            t3_requirements_by_career.get(
                career.id,
                (),
            )
        )

        if (
            len(t1_requirements)
            != len(t3_requirements)
        ):
            mismatches.append(
                (
                    career.name,
                    len(t1_requirements),
                    len(t3_requirements),
                )
            )

    if mismatches:
        raise ValueError(
            "Technology percentage evidence coverage "
            f"does not match T1 evidence: {mismatches}"
        )


def score_profile(
    *,
    profile: TechnologySyntheticBenchmarkProfile,
    careers: tuple[
        Career,
        ...
    ],
    demand_requirements_by_career: dict[
        int,
        tuple[
            TechnologyDemandRequirement,
            ...
        ],
    ],
    idf_weights: dict,
) -> tuple[
    TechnologyCandidate3Result,
    ...
]:
    """
    Score one synthetic profile using Technology Candidate T3.
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
            calculate_technology_candidate_3_fit(
                career_id=career.id,
                career_name=career.name,
                student_proficiencies=(
                    profile.student_proficiencies
                ),
                requirements=(
                    demand_requirements_by_career.get(
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
        rank_technology_candidate_3_results(
            results
        )
    )


def evaluate_profile(
    *,
    profile: TechnologySyntheticBenchmarkProfile,
    ranked_results: tuple[
        TechnologyCandidate3Result,
        ...
    ],
    career_to_group: dict,
) -> TechnologyCandidate3CaseResult:
    """
    Extract exact-Career and O*NET-group rank.
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
            "Target Career missing from Technology T3 results: "
            f"{profile.target_career_name}"
        )

    if target_result.rank is None:
        raise ValueError(
            "Benchmark target Career has no T3 score: "
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

    return TechnologyCandidate3CaseResult(
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
            .technology_fit_score
        ),
        target_alignment_ratio=(
            target_result
            .student_alignment_ratio
        ),
        target_demand_coverage_ratio=(
            target_result
            .demand_coverage_ratio
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


def run_technology_candidate_3_benchmark(
) -> TechnologyCandidate3BenchmarkReport:
    """
    Run T3 over the same evidence-supported benchmark cases
    used by Technology Candidates T1 and T2.
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

    t1_requirements_by_career = (
        load_in_demand_technologies_by_career(
            career_ids=career_ids
        )
    )

    demand_requirements_by_career = (
        load_demand_weighted_technologies_by_career(
            career_ids=career_ids
        )
    )

    validate_requirement_coverage(
        careers=careers,
        t1_requirements_by_career=(
            t1_requirements_by_career
        ),
        t3_requirements_by_career=(
            demand_requirements_by_career
        ),
    )

    benchmark_dataset = (
        build_technology_benchmark_dataset(
            careers=careers,
            requirements_by_career=(
                t1_requirements_by_career
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
                t1_requirements_by_career
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
            demand_requirements_by_career=(
                demand_requirements_by_career
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
            TechnologyCandidate3ScenarioResult(
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

    return TechnologyCandidate3BenchmarkReport(
        model_name=(
            "Technology Candidate T3 - "
            "Demand-Weighted Balanced Fit"
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
