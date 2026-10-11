"""
Career Roadmap overview service.

This service combines:

1. The authoritative deterministic WBS 5.7 Career Roadmap.
2. Student workflow progress stored by the Sprint 3 enhancement.

It does not recalculate:

- Career readiness,
- Skill Gap values,
- roadmap order,
- Career requirements,
- learning-resource matches.

It also does not generate AI guidance.

The output is intended to become the stable backend contract consumed
by the Career Roadmap REST API in a later checkpoint.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from careers.services.learning_roadmap import (
    LearningResourceSummary,
    generate_learning_plan,
)
from careers.services.roadmap_progress import (
    RoadmapProgressSummary,
    reconcile_roadmap_progress,
)


@dataclass(frozen=True)
class RoadmapOverviewStep:
    """
    One deterministic roadmap step with Student workflow progress.
    """

    step_number: int
    skill_id: int
    skill_name: str
    gap_status: object
    current_proficiency: str | None
    current_score: Decimal
    required_level: Decimal
    gap_amount: Decimal
    importance: Decimal
    resources: tuple[
        LearningResourceSummary,
        ...,
    ]
    progress_status: str
    started_at: datetime | None
    completed_at: datetime | None


@dataclass(frozen=True)
class RoadmapOverview:
    """
    Complete internal Career Roadmap result.

    Readiness and roadmap content come from the existing deterministic
    WBS 5.7 LearningPlan.

    Progress comes from RoadmapProgress records.
    """

    student_profile_id: int
    career_id: int
    career_name: str
    score_status: object
    readiness_score: Decimal | None
    progress_summary: (
        RoadmapProgressSummary
    )
    roadmap_steps: tuple[
        RoadmapOverviewStep,
        ...,
    ]


def build_roadmap_overview(
    *,
    plan,
) -> RoadmapOverview:
    """
    Combine one existing LearningPlan with current stored progress.

    The function does not write progress rows.
    Missing progress records appear as not_started.
    """

    progress_snapshot = (
        reconcile_roadmap_progress(
            plan=plan,
        )
    )

    progress_by_skill = {
        step.skill_id: step
        for step
        in progress_snapshot.steps
    }

    overview_steps = []

    for step in plan.roadmap_steps:
        progress = (
            progress_by_skill[
                step.skill_id
            ]
        )

        overview_steps.append(
            RoadmapOverviewStep(
                step_number=(
                    step.step_number
                ),
                skill_id=(
                    step.skill_id
                ),
                skill_name=(
                    step.skill_name
                ),
                gap_status=(
                    step.gap_status
                ),
                current_proficiency=(
                    step.current_proficiency
                ),
                current_score=(
                    step.current_score
                ),
                required_level=(
                    step.required_level
                ),
                gap_amount=(
                    step.gap_amount
                ),
                importance=(
                    step.importance
                ),
                resources=(
                    step.resources
                ),
                progress_status=(
                    progress.status
                ),
                started_at=(
                    progress.started_at
                ),
                completed_at=(
                    progress.completed_at
                ),
            )
        )

    return RoadmapOverview(
        student_profile_id=(
            plan.student_profile_id
        ),
        career_id=(
            plan.career_id
        ),
        career_name=(
            plan.career_name
        ),
        score_status=(
            plan
            .readiness_result
            .score_status
        ),
        readiness_score=(
            plan
            .readiness_result
            .readiness_score
        ),
        progress_summary=(
            progress_snapshot.summary
        ),
        roadmap_steps=tuple(
            overview_steps
        ),
    )


def generate_roadmap_overview(
    *,
    student_profile_id: int,
    career_id: int,
) -> RoadmapOverview:
    """
    Generate the deterministic LearningPlan, then attach workflow progress.

    This is the internal orchestration function the REST API will use
    after the API checkpoint is approved.
    """

    plan = generate_learning_plan(
        student_profile_id=(
            student_profile_id
        ),
        career_id=career_id,
    )

    return build_roadmap_overview(
        plan=plan,
    )
