"""
Career Roadmap progress service.

The deterministic Skill Gap Analysis remains authoritative for:

- roadmap membership,
- roadmap ordering,
- readiness,
- gap values,
- priority.

This service stores only Student workflow progress.

Progress is keyed by Student Profile, Career, and Skill rather than
displayed step number. A changed roadmap order therefore does not move
progress to the wrong Skill.

Stored progress for Skills no longer present in the current roadmap is
preserved as history but excluded from the current progress result.
"""

from dataclasses import dataclass
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from careers.models import RoadmapProgress


class RoadmapStepNotFoundError(ValueError):
    """
    Raised when a requested Skill is not part of the current roadmap.
    """


class RoadmapProgressTransitionError(
    ValueError
):
    """
    Raised when a requested progress transition is not valid.
    """


@dataclass(frozen=True)
class RoadmapStepProgress:
    """
    Progress state for one current roadmap step.
    """

    step_number: int
    skill_id: int
    status: str
    started_at: datetime | None
    completed_at: datetime | None


@dataclass(frozen=True)
class RoadmapProgressSummary:
    """
    Aggregate progress counts for the current roadmap only.
    """

    total: int
    completed: int
    in_progress: int
    not_started: int


@dataclass(frozen=True)
class RoadmapProgressSnapshot:
    """
    Current roadmap progress plus aggregate counts.
    """

    steps: tuple[
        RoadmapStepProgress,
        ...,
    ]
    summary: RoadmapProgressSummary


def _validate_positive_identifier(
    value,
    *,
    field_name: str,
) -> int:
    """
    Convert and validate one positive integer identifier.
    """

    try:
        resolved = int(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            f"{field_name} must be a positive integer."
        ) from error

    if resolved <= 0:
        raise ValueError(
            f"{field_name} must be a positive integer."
        )

    return resolved


def _plan_identity(
    plan,
) -> tuple[int, int]:
    """
    Resolve Student Profile and Career identity from a LearningPlan.
    """

    student_profile_id = (
        _validate_positive_identifier(
            getattr(
                plan,
                "student_profile_id",
                None,
            ),
            field_name=(
                "student_profile_id"
            ),
        )
    )

    career_id = (
        _validate_positive_identifier(
            getattr(
                plan,
                "career_id",
                None,
            ),
            field_name="career_id",
        )
    )

    return (
        student_profile_id,
        career_id,
    )


def _current_steps(
    plan,
):
    """
    Return the current deterministic roadmap steps.
    """

    steps = tuple(
        getattr(
            plan,
            "roadmap_steps",
            (),
        )
        or ()
    )

    return steps


def _find_current_step(
    *,
    plan,
    skill_id: int,
):
    """
    Find one Skill in the current deterministic roadmap.
    """

    resolved_skill_id = (
        _validate_positive_identifier(
            skill_id,
            field_name="skill_id",
        )
    )

    for step in _current_steps(
        plan
    ):
        if (
            int(
                step.skill_id
            )
            == resolved_skill_id
        ):
            return step

    raise RoadmapStepNotFoundError(
        "The selected Skill is not part of "
        "the current Career Roadmap."
    )


def _to_step_progress(
    *,
    step,
    record: RoadmapProgress | None,
) -> RoadmapStepProgress:
    """
    Convert one roadmap step and optional stored row to API-ready state.
    """

    if record is None:
        return RoadmapStepProgress(
            step_number=(
                int(
                    step.step_number
                )
            ),
            skill_id=(
                int(
                    step.skill_id
                )
            ),
            status=(
                RoadmapProgress
                .Status
                .NOT_STARTED
            ),
            started_at=None,
            completed_at=None,
        )

    return RoadmapStepProgress(
        step_number=(
            int(
                step.step_number
            )
        ),
        skill_id=(
            int(
                step.skill_id
            )
        ),
        status=record.status,
        started_at=(
            record.started_at
        ),
        completed_at=(
            record.completed_at
        ),
    )


def load_current_roadmap_progress(
    *,
    plan,
) -> tuple[
    RoadmapStepProgress,
    ...,
]:
    """
    Load progress for current roadmap Skills.

    Missing database rows are represented as not_started without
    writing new rows.

    Progress rows for Skills outside the current roadmap are ignored.
    """

    (
        student_profile_id,
        career_id,
    ) = _plan_identity(
        plan
    )

    steps = _current_steps(
        plan
    )

    if not steps:
        return ()

    skill_ids = tuple(
        int(
            step.skill_id
        )
        for step in steps
    )

    records = {
        record.skill_id: record
        for record
        in (
            RoadmapProgress
            .objects
            .filter(
                student_profile_id=(
                    student_profile_id
                ),
                career_id=career_id,
                skill_id__in=(
                    skill_ids
                ),
            )
        )
    }

    return tuple(
        _to_step_progress(
            step=step,
            record=records.get(
                int(
                    step.skill_id
                )
            ),
        )
        for step in steps
    )


def summarize_roadmap_progress(
    progress_steps,
) -> RoadmapProgressSummary:
    """
    Count progress states for the current roadmap.
    """

    steps = tuple(
        progress_steps
    )

    return RoadmapProgressSummary(
        total=len(
            steps
        ),
        completed=sum(
            1
            for step in steps
            if step.status
            == (
                RoadmapProgress
                .Status
                .COMPLETED
            )
        ),
        in_progress=sum(
            1
            for step in steps
            if step.status
            == (
                RoadmapProgress
                .Status
                .IN_PROGRESS
            )
        ),
        not_started=sum(
            1
            for step in steps
            if step.status
            == (
                RoadmapProgress
                .Status
                .NOT_STARTED
            )
        ),
    )


def reconcile_roadmap_progress(
    *,
    plan,
) -> RoadmapProgressSnapshot:
    """
    Build current progress without rewriting roadmap history.

    This is the reconciliation boundary when the deterministic roadmap
    changes:

    - current Skills receive their stored status,
    - current Skills without a row appear as not_started,
    - stored Skills no longer in the roadmap stay in the database,
      but do not appear in the current result.
    """

    steps = (
        load_current_roadmap_progress(
            plan=plan,
        )
    )

    return RoadmapProgressSnapshot(
        steps=steps,
        summary=(
            summarize_roadmap_progress(
                steps
            )
        ),
    )


@transaction.atomic
def start_roadmap_step(
    *,
    plan,
    skill_id: int,
    timestamp=None,
) -> RoadmapStepProgress:
    """
    Start one current roadmap Skill.

    Repeating the same start operation is idempotent.

    A completed step is not silently reopened. A later product feature
    would need an explicit reopen operation.
    """

    (
        student_profile_id,
        career_id,
    ) = _plan_identity(
        plan
    )

    step = _find_current_step(
        plan=plan,
        skill_id=skill_id,
    )

    resolved_timestamp = (
        timestamp
        or timezone.now()
    )

    record, _ = (
        RoadmapProgress
        .objects
        .select_for_update()
        .get_or_create(
            student_profile_id=(
                student_profile_id
            ),
            career_id=career_id,
            skill_id=(
                step.skill_id
            ),
        )
    )

    if (
        record.status
        == (
            RoadmapProgress
            .Status
            .COMPLETED
        )
    ):
        raise (
            RoadmapProgressTransitionError(
                "A completed roadmap step "
                "must not be restarted implicitly."
            )
        )

    if (
        record.status
        == (
            RoadmapProgress
            .Status
            .IN_PROGRESS
        )
    ):
        return _to_step_progress(
            step=step,
            record=record,
        )

    record.status = (
        RoadmapProgress
        .Status
        .IN_PROGRESS
    )

    if (
        record.started_at
        is None
    ):
        record.started_at = (
            resolved_timestamp
        )

    record.completed_at = None

    record.save(
        update_fields=[
            "status",
            "started_at",
            "completed_at",
            "updated_at",
        ]
    )

    return _to_step_progress(
        step=step,
        record=record,
    )


@transaction.atomic
def complete_roadmap_step(
    *,
    plan,
    skill_id: int,
    timestamp=None,
) -> RoadmapStepProgress:
    """
    Complete one current roadmap Skill.

    Completion is a workflow state only.

    It does not alter readiness, Skill Gap values, Student proficiency,
    or Career requirements.

    Repeating completion is idempotent.
    """

    (
        student_profile_id,
        career_id,
    ) = _plan_identity(
        plan
    )

    step = _find_current_step(
        plan=plan,
        skill_id=skill_id,
    )

    resolved_timestamp = (
        timestamp
        or timezone.now()
    )

    record, _ = (
        RoadmapProgress
        .objects
        .select_for_update()
        .get_or_create(
            student_profile_id=(
                student_profile_id
            ),
            career_id=career_id,
            skill_id=(
                step.skill_id
            ),
        )
    )

    if (
        record.status
        == (
            RoadmapProgress
            .Status
            .COMPLETED
        )
    ):
        return _to_step_progress(
            step=step,
            record=record,
        )

    if (
        record.started_at
        is None
    ):
        record.started_at = (
            resolved_timestamp
        )

    record.status = (
        RoadmapProgress
        .Status
        .COMPLETED
    )

    record.completed_at = (
        resolved_timestamp
    )

    record.save(
        update_fields=[
            "status",
            "started_at",
            "completed_at",
            "updated_at",
        ]
    )

    return _to_step_progress(
        step=step,
        record=record,
    )
