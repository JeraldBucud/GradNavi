"""
Side-by-side structural benchmark for GradNavi scoring models.

Models compared:

1. WBS 5.3 Version 1
   Binary Skill presence weighted by O*NET Importance.

2. Candidate 1
   Proficiency-aware requirement attainment weighted by Importance.

3. Candidate 2
   Normalized weighted competency-deficit distance.

Every model is evaluated against exactly the same synthetic profiles.

Metrics are reported for:

- exact GradNavi Career ranking;
- O*NET occupation-group ranking;
- each benchmark scenario;
- overall performance.

No production code or database rows are modified.
"""

from dataclasses import dataclass

from careers.models import Career

from careers.services.recommendation_scoring import (
    load_weighted_competencies_by_career,
)

from careers.scoring_validation.baseline import (
    score_profile_with_v1,
)

from careers.scoring_validation.candidate_1 import (
    calculate_candidate_1_fit,
    load_requirements_by_career,
    rank_candidate_1_results,
)

from careers.scoring_validation.candidate_2 import (
    calculate_candidate_2_fit,
    rank_candidate_2_results,
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
class EvaluationRow:
    """
    One model result for one benchmark profile.
    """

    model_name: str

    scenario: BenchmarkScenario

    target_career_id: int
    target_career_name: str

    exact_rank: int | None
    occupation_group_rank: int | None


@dataclass(frozen=True)
class ModelScenarioMetrics:
    """
    Exact and O*NET-group metrics for one model/scenario.
    """

    model_name: str

    scenario: BenchmarkScenario

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class ModelOverallMetrics:
    """
    Overall exact and O*NET-group metrics for one model.
    """

    model_name: str

    exact_metrics: RankingMetrics

    occupation_group_metrics: RankingMetrics


@dataclass(frozen=True)
class ComparisonReport:
    """
    Complete comparison report.
    """

    rows: tuple[
        EvaluationRow,
        ...
    ]

    scenario_metrics: tuple[
        ModelScenarioMetrics,
        ...
    ]

    overall_metrics: tuple[
        ModelOverallMetrics,
        ...
    ]


MODEL_V1 = "V1"

MODEL_CANDIDATE_1 = "Candidate 1"

MODEL_CANDIDATE_2 = "Candidate 2"


def evaluate_ranked_results(
    *,
    model_name: str,
    profile: SyntheticBenchmarkProfile,
    ranked_results,
    career_to_group: dict,
) -> EvaluationRow:
    """
    Convert ranked model results into benchmark ranks.
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
            "Target Career was missing from "
            f"{model_name} results: "
            f"{profile.target_career_name}"
        )

    ranked_career_ids = tuple(
        result.career_id
        for result in ranked_results
        if result.rank is not None
    )

    occupation_group_rank = (
        find_group_rank(
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
    )

    return EvaluationRow(
        model_name=model_name,
        scenario=profile.scenario,
        target_career_id=(
            profile.target_career_id
        ),
        target_career_name=(
            profile.target_career_name
        ),
        exact_rank=(
            target_result.rank
        ),
        occupation_group_rank=(
            occupation_group_rank
        ),
    )


def score_candidate_1(
    *,
    profile: SyntheticBenchmarkProfile,
    careers: tuple[
        Career,
        ...
    ],
    requirements_by_career: dict,
):
    """
    Score one benchmark profile with Candidate 1.
    """

    results = []

    for career in careers:
        results.append(
            calculate_candidate_1_fit(
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
        )

    return rank_candidate_1_results(
        results
    )


def score_candidate_2(
    *,
    profile: SyntheticBenchmarkProfile,
    careers: tuple[
        Career,
        ...
    ],
    requirements_by_career: dict,
):
    """
    Score one benchmark profile with Candidate 2.
    """

    results = []

    for career in careers:
        results.append(
            calculate_candidate_2_fit(
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
        )

    return rank_candidate_2_results(
        results
    )


def run_model_comparison(
) -> ComparisonReport:
    """
    Run V1, Candidate 1, and Candidate 2 on the same 72 cases.
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

    weighted_competencies = (
        load_weighted_competencies_by_career(
            career_ids=career_ids
        )
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

    rows = []

    for profile in profiles:
        v1_results = (
            score_profile_with_v1(
                profile=profile,
                careers=careers,
                competencies_by_career=(
                    weighted_competencies
                ),
            )
        )

        rows.append(
            evaluate_ranked_results(
                model_name=MODEL_V1,
                profile=profile,
                ranked_results=v1_results,
                career_to_group=(
                    career_to_group
                ),
            )
        )

        candidate_1_results = (
            score_candidate_1(
                profile=profile,
                careers=careers,
                requirements_by_career=(
                    requirements_by_career
                ),
            )
        )

        rows.append(
            evaluate_ranked_results(
                model_name=(
                    MODEL_CANDIDATE_1
                ),
                profile=profile,
                ranked_results=(
                    candidate_1_results
                ),
                career_to_group=(
                    career_to_group
                ),
            )
        )

        candidate_2_results = (
            score_candidate_2(
                profile=profile,
                careers=careers,
                requirements_by_career=(
                    requirements_by_career
                ),
            )
        )

        rows.append(
            evaluate_ranked_results(
                model_name=(
                    MODEL_CANDIDATE_2
                ),
                profile=profile,
                ranked_results=(
                    candidate_2_results
                ),
                career_to_group=(
                    career_to_group
                ),
            )
        )

    rows_tuple = tuple(
        rows
    )

    model_names = (
        MODEL_V1,
        MODEL_CANDIDATE_1,
        MODEL_CANDIDATE_2,
    )

    scenario_metrics = []

    for model_name in model_names:
        for scenario in BenchmarkScenario:
            selected = tuple(
                row
                for row in rows_tuple
                if (
                    row.model_name
                    == model_name
                    and row.scenario
                    == scenario
                )
            )

            exact_metrics = (
                calculate_ranking_metrics(
                    row.exact_rank
                    for row in selected
                )
            )

            group_metrics = (
                calculate_ranking_metrics(
                    row.occupation_group_rank
                    for row in selected
                )
            )

            scenario_metrics.append(
                ModelScenarioMetrics(
                    model_name=(
                        model_name
                    ),
                    scenario=(
                        scenario
                    ),
                    exact_metrics=(
                        exact_metrics
                    ),
                    occupation_group_metrics=(
                        group_metrics
                    ),
                )
            )

    overall_metrics = []

    for model_name in model_names:
        selected = tuple(
            row
            for row in rows_tuple
            if row.model_name
            == model_name
        )

        exact_metrics = (
            calculate_ranking_metrics(
                row.exact_rank
                for row in selected
            )
        )

        group_metrics = (
            calculate_ranking_metrics(
                row.occupation_group_rank
                for row in selected
            )
        )

        overall_metrics.append(
            ModelOverallMetrics(
                model_name=model_name,
                exact_metrics=(
                    exact_metrics
                ),
                occupation_group_metrics=(
                    group_metrics
                ),
            )
        )

    return ComparisonReport(
        rows=rows_tuple,
        scenario_metrics=tuple(
            scenario_metrics
        ),
        overall_metrics=tuple(
            overall_metrics
        ),
    )