from collections import defaultdict

from django.db.models import Count

from careers.services.readiness_scoring import (
    CareerNotAvailableError,
    CareerNotFoundError,
    GapStatus,
    calculate_selected_career_readiness,
)
from profiles.models import CareerGoal


def get_admin_analytics():
    """
    Build aggregated FR-15 administration analytics.

    Results intentionally contain no per-student rows or identifiers.
    """

    return {
        "popular_careers": (
            _popular_career_selections()
        ),
        "common_skill_gaps": (
            _common_skill_gaps()
        ),
    }


def _popular_career_selections():
    rows = (
        CareerGoal.objects
        .filter(
            career__isnull=False,
        )
        .values(
            "career_id",
            "career__name",
        )
        .annotate(
            selection_count=Count("id"),
        )
        .order_by(
            "-selection_count",
            "career__name",
            "career_id",
        )
    )

    return [
        {
            "career_id": row["career_id"],
            "career_name": row["career__name"],
            "selection_count": (
                row["selection_count"]
            ),
        }
        for row in rows
    ]


def _common_skill_gaps():
    affected_students_by_skill = defaultdict(set)
    skill_names = {}

    career_goals = (
        CareerGoal.objects
        .filter(
            career__isnull=False,
        )
        .select_related(
            "career",
            "student_profile",
        )
        .order_by(
            "student_profile_id",
            "career_id",
        )
    )

    for goal in career_goals:
        try:
            result = (
                calculate_selected_career_readiness(
                    student_profile_id=(
                        goal.student_profile_id
                    ),
                    career_id=goal.career_id,
                )
            )

        except (
            CareerNotAvailableError,
            CareerNotFoundError,
        ):
            continue

        for gap in result.skill_gaps:
            if gap.gap_status not in (
                GapStatus.MISSING,
                GapStatus.BELOW_REQUIREMENT,
            ):
                continue

            skill_names[gap.skill_id] = (
                gap.skill_name
            )
            affected_students_by_skill[
                gap.skill_id
            ].add(
                goal.student_profile_id
            )

    rows = [
        {
            "skill_id": skill_id,
            "skill_name": skill_names[skill_id],
            "affected_student_count": len(
                student_ids
            ),
        }
        for skill_id, student_ids
        in affected_students_by_skill.items()
    ]

    rows.sort(
        key=lambda row: (
            -row["affected_student_count"],
            row["skill_name"].casefold(),
            row["skill_id"],
        )
    )

    return rows
