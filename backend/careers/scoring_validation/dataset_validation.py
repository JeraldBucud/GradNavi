"""
Dataset-backed validation for the selected Candidate 2 model.

Unlike the isolated unit tests, these checks inspect the actual active
GradNavi Reference Dataset currently loaded in PostgreSQL.

They verify known structural facts discovered during scoring research:

1. DevOps Engineer and Software Engineer share identical O*NET
   numerical competency vectors.

2. Because those vectors are identical, Candidate 2 must give them
   exactly the same O*NET competency fit for the same Student profile.

3. Health Information Manager currently has no eligible numerical
   O*NET evidence and therefore must return insufficient_evidence.

4. Dataset 1.0 currently contains numerical evidence for 35 of the
   36 active GradNavi Careers.

These checks perform database reads only.
"""

from dataclasses import dataclass
from decimal import Decimal

from careers.models import Career
from careers.services.recommendation_scoring import (
    ScoreStatus,
)

from careers.scoring_validation.candidate_1 import (
    load_requirements_by_career,
)

from careers.scoring_validation.candidate_2 import (
    calculate_candidate_2_fit,
)

from careers.scoring_validation.synthetic_profiles import (
    BenchmarkScenario,
    build_benchmark_profile,
)


@dataclass(frozen=True)
class DatasetValidationReport:
    """
    Summary of Candidate 2 checks against the active dataset.
    """

    active_career_count: int

    careers_with_numerical_evidence: int

    careers_without_numerical_evidence: int

    careers_without_numerical_evidence_names: tuple[
        str,
        ...
    ]

    software_engineer_requirement_count: int

    devops_requirement_count: int

    software_devops_vectors_identical: bool

    software_engineer_score: Decimal

    devops_engineer_score: Decimal

    software_devops_scores_identical: bool

    health_information_manager_status: ScoreStatus


def requirement_signature(
    requirements,
) -> tuple:
    """
    Return a deterministic numerical-evidence signature.

    The signature contains exactly the fields Candidate 2 uses:

    - canonical Skill ID;
    - source domain;
    - Importance;
    - required Level.
    """

    return tuple(
        sorted(
            (
                requirement.skill_id,
                requirement.source_domain,
                requirement.importance,
                requirement.required_level,
            )
            for requirement
            in requirements
        )
    )


def run_candidate_2_dataset_validation(
) -> DatasetValidationReport:
    """
    Validate Candidate 2 against the active GradNavi dataset.

    Raises AssertionError if a known dataset/scoring invariant fails.
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
        raise AssertionError(
            "No active GradNavi Careers were found."
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

    careers_without_evidence = tuple(
        career
        for career in careers
        if not requirements_by_career.get(
            career.id,
            (),
        )
    )

    careers_with_evidence_count = (
        len(careers)
        - len(careers_without_evidence)
    )

    software_engineer = next(
        career
        for career in careers
        if career.name
        == "Software Engineer"
    )

    devops_engineer = next(
        career
        for career in careers
        if career.name
        == "DevOps Engineer"
    )

    health_information_manager = next(
        career
        for career in careers
        if career.name
        == "Health Information Manager"
    )

    software_requirements = (
        requirements_by_career.get(
            software_engineer.id,
            (),
        )
    )

    devops_requirements = (
        requirements_by_career.get(
            devops_engineer.id,
            (),
        )
    )

    health_requirements = (
        requirements_by_career.get(
            health_information_manager.id,
            (),
        )
    )

    software_signature = (
        requirement_signature(
            software_requirements
        )
    )

    devops_signature = (
        requirement_signature(
            devops_requirements
        )
    )

    vectors_identical = (
        software_signature
        == devops_signature
    )

    # Build a source-backed synthetic Software Engineer profile.
    software_profile = (
        build_benchmark_profile(
            career=software_engineer,
            scenario=(
                BenchmarkScenario.FULL_COMPETENCY
            ),
        )
    )

    software_result = (
        calculate_candidate_2_fit(
            career_id=(
                software_engineer.id
            ),
            career_name=(
                software_engineer.name
            ),
            student_proficiencies=(
                software_profile
                .student_proficiencies
            ),
            requirements=(
                software_requirements
            ),
        )
    )

    devops_result = (
        calculate_candidate_2_fit(
            career_id=(
                devops_engineer.id
            ),
            career_name=(
                devops_engineer.name
            ),
            student_proficiencies=(
                software_profile
                .student_proficiencies
            ),
            requirements=(
                devops_requirements
            ),
        )
    )

    health_result = (
        calculate_candidate_2_fit(
            career_id=(
                health_information_manager.id
            ),
            career_name=(
                health_information_manager.name
            ),
            student_proficiencies=(
                software_profile
                .student_proficiencies
            ),
            requirements=(
                health_requirements
            ),
        )
    )

    scores_identical = (
        software_result.career_fit_score
        == devops_result.career_fit_score
        and
        software_result.normalized_deficit
        == devops_result.normalized_deficit
    )

    # Dataset invariants discovered during the scoring audit.
    assert len(careers) == 36, (
        "Expected 36 active GradNavi Careers, "
        f"found {len(careers)}."
    )

    assert careers_with_evidence_count == 35, (
        "Expected numerical O*NET evidence for "
        f"35 Careers, found {careers_with_evidence_count}."
    )

    assert len(
        careers_without_evidence
    ) == 1, (
        "Expected exactly one Career without "
        "numerical O*NET evidence."
    )

    assert (
        careers_without_evidence[0].name
        == "Health Information Manager"
    ), (
        "Expected Health Information Manager "
        "to be the Career without numerical evidence."
    )

    assert len(
        software_requirements
    ) == 45, (
        "Expected Software Engineer to have "
        f"45 numerical requirements, found "
        f"{len(software_requirements)}."
    )

    assert len(
        devops_requirements
    ) == 45, (
        "Expected DevOps Engineer to have "
        f"45 numerical requirements, found "
        f"{len(devops_requirements)}."
    )

    assert vectors_identical, (
        "Software Engineer and DevOps Engineer "
        "no longer have identical O*NET numerical vectors."
    )

    assert (
        software_result.score_status
        == ScoreStatus.SCORED
    )

    assert (
        devops_result.score_status
        == ScoreStatus.SCORED
    )

    assert scores_identical, (
        "Identical O*NET vectors produced different "
        "Candidate 2 scores."
    )

    assert (
        health_result.score_status
        == ScoreStatus.INSUFFICIENT_EVIDENCE
    ), (
        "Health Information Manager must remain "
        "insufficient_evidence while numerical O*NET "
        "evidence is unavailable."
    )

    return DatasetValidationReport(
        active_career_count=(
            len(careers)
        ),
        careers_with_numerical_evidence=(
            careers_with_evidence_count
        ),
        careers_without_numerical_evidence=(
            len(
                careers_without_evidence
            )
        ),
        careers_without_numerical_evidence_names=tuple(
            career.name
            for career
            in careers_without_evidence
        ),
        software_engineer_requirement_count=(
            len(
                software_requirements
            )
        ),
        devops_requirement_count=(
            len(
                devops_requirements
            )
        ),
        software_devops_vectors_identical=(
            vectors_identical
        ),
        software_engineer_score=(
            software_result
            .career_fit_score
        ),
        devops_engineer_score=(
            devops_result
            .career_fit_score
        ),
        software_devops_scores_identical=(
            scores_identical
        ),
        health_information_manager_status=(
            health_result
            .score_status
        ),
    )