"""
Learning Resource recommendation service for GradNavi.

The approved LearningResourceSkill relationship is the relevance gate.

Ranking rules:

1. Resource must be active.
2. Resource health must be Active.
3. Resource must be linked to the requested Skill.
4. Helpful feedback improves ranking.
5. Not Helpful feedback lowers ranking.
6. Verified resources rank ahead when feedback signals are equal.
7. Free ranks ahead of Freemium, Paid, then Unknown when stronger
   quality signals are equal.
8. Unknown stays eligible during catalogue classification.
9. A maximum of 12 resources is returned for one Skill.
10. No minimum count is forced.
11. No access-category quota is forced.
12. Reports do not directly remove resources.
13. This service performs no generative AI calls.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from django.db.models import (
    Count,
    Q,
)

from careers.models import (
    LearningResource,
    LearningResourceFeedback,
)


MAX_RESOURCES_PER_SKILL = 12


ACCESS_PRIORITY = {
    LearningResource.AccessType.FREE: 0,
    LearningResource.AccessType.FREEMIUM: 1,
    LearningResource.AccessType.PAID: 2,
    LearningResource.AccessType.UNKNOWN: 3,
}


@dataclass(frozen=True)
class RankedLearningResource:
    id: int
    title: str
    provider: str
    url: str
    resource_type: str
    access_type: str
    source_type: str
    health_status: str
    description: str
    last_checked_at: datetime | None
    last_verified_at: datetime | None
    helpful_count: int
    not_helpful_count: int
    feedback_score: int
    why_this_fits: str


def _validate_skill_id(
    skill_id,
) -> int:
    try:
        value = int(
            skill_id
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            "skill_id must be a positive integer."
        ) from error

    if value <= 0:
        raise ValueError(
            "skill_id must be a positive integer."
        )

    return value


def _validate_limit(
    limit,
) -> int:
    try:
        value = int(
            limit
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            "limit must be a positive integer."
        ) from error

    if value <= 0:
        raise ValueError(
            "limit must be a positive integer."
        )

    return min(
        value,
        MAX_RESOURCES_PER_SKILL,
    )


def _normalize_access_types(
    access_types: Iterable[str] | None,
) -> tuple[str, ...] | None:

    if access_types is None:
        return None

    allowed = set(
        LearningResource
        .AccessType
        .values
    )

    values = tuple(
        dict.fromkeys(
            str(item)
            .strip()
            .lower()
            for item
            in access_types
        )
    )

    invalid = tuple(
        item
        for item
        in values
        if item not in allowed
    )

    if invalid:
        raise ValueError(
            "Invalid learning-resource access type: "
            f"{invalid}."
        )

    return values


def build_why_this_fits(
    *,
    resource: LearningResource,
    skill_name: str,
    career_name: str | None = None,
) -> str:
    """
    Build grounded fallback text without an AI call.

    Richer AI personalisation will sit above this service.
    """

    resolved_skill_name = (
        str(
            skill_name
        )
        .strip()
    )

    if not resolved_skill_name:
        raise ValueError(
            "skill_name must not be blank."
        )

    career_suffix = ""

    if (
        career_name is not None
        and str(
            career_name
        ).strip()
    ):
        career_suffix = (
            " for "
            + str(
                career_name
            ).strip()
        )

    access_label = {
        LearningResource
        .AccessType
        .FREE: "Free",
        LearningResource
        .AccessType
        .FREEMIUM: "Freemium",
        LearningResource
        .AccessType
        .PAID: "Paid",
    }.get(
        resource.access_type
    )

    resource_type = (
        resource
        .get_resource_type_display()
        .lower()
    )

    if access_label:
        return (
            f"{access_label} {resource_type} matched to your "
            f"{resolved_skill_name} skill gap"
            f"{career_suffix}."
        )

    return (
        "Matched to your "
        f"{resolved_skill_name} skill gap"
        f"{career_suffix}."
    )


def _ranking_key(
    resource,
):
    helpful = int(
        resource.helpful_count
        or 0
    )

    not_helpful = int(
        resource.not_helpful_count
        or 0
    )

    feedback_score = (
        helpful
        - not_helpful
    )

    verification_rank = (
        0
        if resource.last_verified_at
        is not None
        else 1
    )

    access_rank = (
        ACCESS_PRIORITY.get(
            resource.access_type,
            ACCESS_PRIORITY[
                LearningResource
                .AccessType
                .UNKNOWN
            ],
        )
    )

    return (
        -feedback_score,
        -helpful,
        not_helpful,
        verification_rank,
        access_rank,
        resource.title.casefold(),
        resource.provider.casefold(),
        resource.id,
    )


def load_ranked_learning_resources(
    *,
    skill_id: int,
    skill_name: str,
    career_name: str | None = None,
    access_types: Iterable[str] | None = None,
    limit: int = MAX_RESOURCES_PER_SKILL,
) -> tuple[
    RankedLearningResource,
    ...,
]:

    resolved_skill_id = (
        _validate_skill_id(
            skill_id
        )
    )

    resolved_limit = (
        _validate_limit(
            limit
        )
    )

    resolved_access_types = (
        _normalize_access_types(
            access_types
        )
    )

    queryset = (
        LearningResource
        .objects
        .filter(
            is_active=True,
            health_status=(
                LearningResource
                .HealthStatus
                .ACTIVE
            ),
            skill_links__skill_id=(
                resolved_skill_id
            ),
        )
        .annotate(
            helpful_count=Count(
                "student_feedback",
                filter=Q(
                    student_feedback__feedback_type=(
                        LearningResourceFeedback
                        .FeedbackType
                        .HELPFUL
                    ),
                ),
                distinct=True,
            ),
            not_helpful_count=Count(
                "student_feedback",
                filter=Q(
                    student_feedback__feedback_type=(
                        LearningResourceFeedback
                        .FeedbackType
                        .NOT_HELPFUL
                    ),
                ),
                distinct=True,
            ),
        )
        .distinct()
    )

    if (
        resolved_access_types
        is not None
    ):
        queryset = queryset.filter(
            access_type__in=(
                resolved_access_types
            )
        )

    ranked = sorted(
        queryset,
        key=_ranking_key,
    )

    selected = ranked[
        :resolved_limit
    ]

    return tuple(
        RankedLearningResource(
            id=resource.id,
            title=resource.title,
            provider=resource.provider,
            url=resource.url,
            resource_type=(
                resource.resource_type
            ),
            access_type=(
                resource.access_type
            ),
            source_type=(
                resource.source_type
            ),
            health_status=(
                resource.health_status
            ),
            description=(
                resource.description
            ),
            last_checked_at=(
                resource.last_checked_at
            ),
            last_verified_at=(
                resource.last_verified_at
            ),
            helpful_count=int(
                resource.helpful_count
                or 0
            ),
            not_helpful_count=int(
                resource.not_helpful_count
                or 0
            ),
            feedback_score=(
                int(
                    resource.helpful_count
                    or 0
                )
                - int(
                    resource.not_helpful_count
                    or 0
                )
            ),
            why_this_fits=(
                build_why_this_fits(
                    resource=resource,
                    skill_name=skill_name,
                    career_name=career_name,
                )
            ),
        )
        for resource
        in selected
    )
