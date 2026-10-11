"""
GradNavi WBS 5.3 Version 1 baseline benchmark.

This module evaluates the existing production recommendation formula
without modifying it.

The benchmark calls the same pure calculation and ranking functions
used by production WBS 5.3.

No StudentProfile records are created.
No database rows are modified.
"""

from dataclasses import dataclass
from decimal import Decimal

from careers.models import Career
from careers.services.recommendation_scoring import (
    RecommendationResult,
    calculate_career_fit,
    load_weighted_competencies_by_career,
    rank_recommendation_results,
)

from careers.scoring_validation.metrics import (
    RankingMetrics,
    calculate_ranking_metrics,
)

from careers.scoring_validation.synthetic_profiles import (
    BenchmarkScenario,
    SyntheticBenchmarkProfile,
    build_all_benchmark_profiles,
)


@dataclass(frozen=True)
class BaselineCaseResult:
    """
    Result of one synthetic benchmark profile.
    """

    target_career_id: int
    target_career_name: str

    scenario: BenchmarkScenario

    target_rank: int | None

    target_score: Decimal | None

    profile_skill_count: int


@dataclass(frozen=True)
class ScenarioBaselineResult:
    """
    Aggregate metrics for one benchmark scenario.
    """

    scenario: BenchmarkScenario

    case_count: int

    metrics: RankingMetrics


@dataclass(frozen=True)
class BaselineReport:
    """
    Complete V1 benchmark report.
    """

    model_name: str

    case_results: tuple[
        BaselineCaseResult,
        ...
    ]

    scenario_results: tuple[
        ScenarioBaselineResult,
        ...
    ]

    overall_metrics: RankingMetrics


def score_profile_with_v1(
    *,
    profile: SyntheticBenchmarkProfile,
    careers: tuple[Career, ...],
    competencies_by_career: dict,
) -> tuple[RecommendationResult, ...]:
    """
    Score one synthetic profile using untouched production V1 logic.

    This deliberately calls:

    calculate_career_fit()
    rank_recommendation_results()

    from production WBS 5.3.
    """

    results = []

    for career in careers:
        result = calculate_career_fit(
            career_id=career.id,
            career_name=career.name,
            student_skill_ids=(
                profile.student_skill_ids
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


def evaluate_profile(
    *,
    profile: SyntheticBenchmarkProfile,
    ranked_results: tuple[
        RecommendationResult,
        ...
    ],
) -> BaselineCaseResult:
    """
    Extract the expected Career's score and rank.
    """

    target_result = next(
        (
            result
            for result in ranked_results
            if result.career_id
            == profile.target_career_id
        ),
        None,
    )

    if target_result is None:
        raise ValueError(
            "Target Career was missing "
            "from recommendation results: "
            f"{profile.target_career_name}"
        )

    return BaselineCaseResult(
        target_career_id=(
            profile.target_career_id
        ),
        target_career_name=(
            profile.target_career_name
        ),
        scenario=profile.scenario,
        target_rank=target_result.rank,
        target_score=(
            target_result
            .recommendation_score
        ),
        profile_skill_count=(
            len(profile.skills)
        ),
    )


def run_v1_baseline() -> BaselineReport:
    """
    Execute the complete 72-case V1 structural benchmark.
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

    profiles = (
        build_all_benchmark_profiles()
    )

    case_results = []

    for profile in profiles:
        ranked_results = (
            score_profile_with_v1(
                profile=profile,
                careers=careers,
                competencies_by_career=(
                    competencies_by_career
                ),
            )
        )

        case_results.append(
            evaluate_profile(
                profile=profile,
                ranked_results=(
                    ranked_results
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
            for result in case_results_tuple
            if result.scenario
            == scenario
        )

        scenario_metrics = (
            calculate_ranking_metrics(
                result.target_rank
                for result in scenario_cases
            )
        )

        scenario_results.append(
            ScenarioBaselineResult(
                scenario=scenario,
                case_count=(
                    len(scenario_cases)
                ),
                metrics=(
                    scenario_metrics
                ),
            )
        )

    overall_metrics = (
        calculate_ranking_metrics(
            result.target_rank
            for result in case_results_tuple
        )
    )

    return BaselineReport(
        model_name=(
            "WBS 5.3 Version 1"
        ),
        case_results=(
            case_results_tuple
        ),
        scenario_results=tuple(
            scenario_results
        ),
        overall_metrics=(
            overall_metrics
        ),
    )