"""
Resolve an authorized target Career for document generation.

A target Career is available when:

1. The Career is active.
2. The authenticated Student has saved the Career as a structured
   Career Goal, or
3. The Career exists in the Student's current valid Career
   Recommendation snapshot.

Client-supplied Career names are not trusted.
The canonical Career name always comes from the GradNavi database.
"""

from careers.models import Career
from careers.services.recommendation_cache import (
    build_recommendation_cache_key,
    get_valid_recommendation_snapshot,
)
from profiles.models import CareerGoal, StudentProfile


class TargetCareerNotAvailableError(Exception):
    """
    Raised when a requested document target Career is unavailable
    to the authenticated Student.
    """


def _normalized_positive_career_id(
    career_id,
) -> int:
    if isinstance(
        career_id,
        bool,
    ):
        raise TargetCareerNotAvailableError(
            "Selected target career is not available."
        )

    try:
        normalized_id = int(
            career_id,
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise TargetCareerNotAvailableError(
            "Selected target career is not available."
        ) from exc

    if normalized_id <= 0:
        raise TargetCareerNotAvailableError(
            "Selected target career is not available."
        )

    return normalized_id


def _snapshot_contains_career(
    payload,
    career_id,
) -> bool:
    if not isinstance(
        payload,
        dict,
    ):
        return False

    recommendations = payload.get(
        "recommendations",
    )

    if not isinstance(
        recommendations,
        list,
    ):
        return False

    for recommendation in recommendations:
        if not isinstance(
            recommendation,
            dict,
        ):
            continue

        recommendation_career_id = (
            recommendation.get(
                "career_id"
            )
        )

        try:
            normalized_recommendation_id = int(
                recommendation_career_id,
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        if (
            normalized_recommendation_id
            == career_id
        ):
            return True

    return False


def _student_has_saved_career_goal(
    *,
    student_profile: StudentProfile,
    career: Career,
) -> bool:
    return (
        CareerGoal.objects.filter(
            student_profile=student_profile,
            career_id=career.id,
        ).exists()
    )


def _student_has_valid_recommendation(
    *,
    student_profile: StudentProfile,
    career_id: int,
) -> bool:
    cache_key = (
        build_recommendation_cache_key(
            student_profile=student_profile,
        )
    )

    snapshot = (
        get_valid_recommendation_snapshot(
            student_profile=student_profile,
            cache_key=cache_key,
        )
    )

    if snapshot is None:
        return False

    return _snapshot_contains_career(
        snapshot.payload,
        career_id,
    )


def resolve_document_target_career(
    *,
    student_profile: StudentProfile,
    career_id,
) -> Career:
    """
    Return the canonical active Career authorized for this Student.

    The caller supplies only a Career identifier. The Career name used
    by document generation always comes from the database.
    """

    normalized_id = (
        _normalized_positive_career_id(
            career_id,
        )
    )

    try:
        career = Career.objects.get(
            pk=normalized_id,
            active=True,
        )
    except Career.DoesNotExist as exc:
        raise TargetCareerNotAvailableError(
            "Selected target career is not available."
        ) from exc

    if _student_has_saved_career_goal(
        student_profile=student_profile,
        career=career,
    ):
        return career

    if _student_has_valid_recommendation(
        student_profile=student_profile,
        career_id=career.id,
    ):
        return career

    raise TargetCareerNotAvailableError(
        "Selected target career is not available."
    )
