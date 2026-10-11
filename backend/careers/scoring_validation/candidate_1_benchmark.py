"""
Benchmark runner for GradNavi Candidate 1.

Candidate 1 uses:

- O*NET competency Importance;
- O*NET required Level;
- GradNavi Student proficiency;
- capped requirement attainment.

The benchmark evaluates both:

1. Exact GradNavi Career ranking.
2. O*NET occupation-group ranking.

This distinction is necessary because multiple GradNavi Careers may
share exactly the same O*NET occupation evidence.

No production code or database records are modified.
"""

from dataclasses import dataclass
from decimal import Decimal

from careers.models import Career

from careers.scoring_validation.candidate_1 import (
    Candidate1Result,
    calculate_candidate_1_fit,
    load_requirements_by_career,
    rank_candidate_1_results,
)

from careers.scoring_validation.metrics import (
    RankingMetrics,
    calculate_ranking_metrics,
)

from careers.scoring_validation.occupation_groups import (
    build_career_to_group_map,
    find_group_rank,
)

from careers.scoring_validation.synthetic_profiles import (
    BenchmarkScenario,
    SyntheticBenchmarkProfile,
    build_all_benchmark_profiles,
)


@dataclass(frozen=True)
class Candidate1CaseResult:
    """
    One Candidate 1 benchmark case.
    """

    target_career_id: int
    target_career_name: str

    scenario: BenchmarkScenario

    exact_rank: int | None
    occupation_group_rank: int | None

    target_score: Decimal | None

    profile_skill_count: int


@dataclass(frozen=True)
class Candidate1ScenarioResult:
    """
    Aggregate Candidate 1 metrics for one benchmark scenario.
    """

    scenario: BenchmarkScenario

    case_count: int

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class Candidate1BenchmarkReport:
    """
    Complete Candidate 1 structural benchmark report.
    """

    model_name: str

    case_results: tuple[
        Candidate1CaseResult,
        ...
    ]

    scenario_results: tuple[
        Candidate1ScenarioResult,
        ...
    ]

    overall_exact_metrics: RankingMetrics

    overall_occupation_group_metrics: RankingMetrics


def score_profile(
    *,
    profile: SyntheticBenchmarkProfile,
    careers: tuple[
        Career,
        ...
    ],
    requirements_by_career: dict,
) -> tuple[
    Candidate1Result,
    ...
]:
    """
    Score one synthetic profile using Candidate 1.
    """

    results = []

    for career in careers:
        result = calculate_candidate_1_fit(
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
        )

        results.append(
            result
        )

    return rank_candidate_1_results(
        results
    )


def evaluate_profile(
    *,
    profile: SyntheticBenchmarkProfile,
    ranked_results: tuple[
        Candidate1Result,
        ...
    ],
    career_to_group: dict,
) -> Candidate1CaseResult:
    """
    Extract exact-Career and occupation-group ranking.
    """

    target_result = next(
        (
            result
            for result in ranked_results
            if (
                result.career_id
                == profile.target_career_id
            )
        ),
        None,
    )

    if target_result is None:
        raise ValueError(
            "Target Career was missing "
            "from Candidate 1 results: "
            f"{profile.target_career_name}"
        )

    ranked_career_ids = tuple(
        result.career_id
        for result in ranked_results
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

    return Candidate1CaseResult(
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
            .career_fit_score
        ),
        profile_skill_count=(
            len(profile.skills)
        ),
    )


def run_candidate_1_benchmark(
) -> Candidate1BenchmarkReport:
    """
    Run Candidate 1 over the same 72 structural benchmark cases.
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

    requirements_by_career = (
        load_requirements_by_career(
            career_ids=career_ids
        )
    )

    career_to_group = (
        build_career_to_group_map()
    )

    profiles = (
        build_all_benchmark_profiles()
    )

    case_results = []

    for profile in profiles:
        ranked_results = score_profile(
            profile=profile,
            careers=careers,
            requirements_by_career=(
                requirements_by_career
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

    for scenario in BenchmarkScenario:
        scenario_cases = tuple(
            result
            for result
            in case_results_tuple
            if result.scenario
            == scenario
        )

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
            Candidate1ScenarioResult(
                scenario=scenario,
                case_count=(
                    len(scenario_cases)
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

    return Candidate1BenchmarkReport(
        model_name=(
            "Candidate 1 - "
            "Proficiency-Aware O*NET Attainment"
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