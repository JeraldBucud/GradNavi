"""
Student interaction service for GradNavi Learning Resources.

This service owns:

- Helpful feedback
- Not Helpful feedback
- Student issue reports
- current Student feedback lookup

Student feedback affects ranking.

Student reports enter review only.
A Student report never directly hides or archives a resource.
"""

from dataclasses import dataclass

from django.db import transaction
from django.db.models import (
    Count,
    Q,
)

from careers.models import (
    LearningResource,
    LearningResourceFeedback,
    LearningResourceReport,
)


class LearningResourceUnavailableError(
    ValueError
):
    """
    Raised when a Student-facing resource does not exist
    or is not currently available.
    """


@dataclass(frozen=True)
class LearningResourceFeedbackResult:
    resource_id: int
    feedback_type: str
    helpful_count: int
    not_helpful_count: int


@dataclass(frozen=True)
class LearningResourceReportResult:
    report_id: int
    resource_id: int
    reason: str
    status: str
    created: bool


def _get_available_resource(
    resource_id,
):
    try:
        resolved_id = int(
            resource_id
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise (
            LearningResourceUnavailableError(
                "Learning Resource was not found."
            )
        ) from error

    if resolved_id <= 0:
        raise (
            LearningResourceUnavailableError(
                "Learning Resource was not found."
            )
        )

    resource = (
        LearningResource
        .objects
        .filter(
            id=resolved_id,
            is_active=True,
            health_status=(
                LearningResource
                .HealthStatus
                .ACTIVE
            ),
        )
        .first()
    )

    if resource is None:
        raise (
            LearningResourceUnavailableError(
                "Learning Resource was not found."
            )
        )

    return resource


def _feedback_counts(
    resource,
):
    counts = (
        resource
        .student_feedback
        .aggregate(
            helpful_count=Count(
                "id",
                filter=Q(
                    feedback_type=(
                        LearningResourceFeedback
                        .FeedbackType
                        .HELPFUL
                    ),
                ),
            ),
            not_helpful_count=Count(
                "id",
                filter=Q(
                    feedback_type=(
                        LearningResourceFeedback
                        .FeedbackType
                        .NOT_HELPFUL
                    ),
                ),
            ),
        )
    )

    return (
        int(
            counts[
                "helpful_count"
            ]
            or 0
        ),
        int(
            counts[
                "not_helpful_count"
            ]
            or 0
        ),
    )


@transaction.atomic
def set_learning_resource_feedback(
    *,
    student_profile,
    resource_id,
    feedback_type,
):
    """
    Store one current usefulness response.

    Repeating the same response is idempotent.

    Changing Helpful to Not Helpful, or the reverse,
    updates the existing row.
    """

    allowed = {
        LearningResourceFeedback
        .FeedbackType
        .HELPFUL,
        LearningResourceFeedback
        .FeedbackType
        .NOT_HELPFUL,
    }

    if feedback_type not in allowed:
        raise ValueError(
            "Invalid Learning Resource feedback type."
        )

    resource = (
        _get_available_resource(
            resource_id
        )
    )

    feedback, _ = (
        LearningResourceFeedback
        .objects
        .update_or_create(
            student_profile=(
                student_profile
            ),
            learning_resource=(
                resource
            ),
            defaults={
                "feedback_type": (
                    feedback_type
                ),
            },
        )
    )

    (
        helpful_count,
        not_helpful_count,
    ) = _feedback_counts(
        resource
    )

    return (
        LearningResourceFeedbackResult(
            resource_id=(
                resource.id
            ),
            feedback_type=(
                feedback.feedback_type
            ),
            helpful_count=(
                helpful_count
            ),
            not_helpful_count=(
                not_helpful_count
            ),
        )
    )


def load_student_feedback_by_resource(
    *,
    student_profile_id,
    resource_ids,
):
    """
    Return the current Student feedback for supplied resources.
    """

    ids = tuple(
        dict.fromkeys(
            int(
                resource_id
            )
            for resource_id
            in resource_ids
        )
    )

    if not ids:
        return {}

    return {
        resource_id: feedback_type
        for (
            resource_id,
            feedback_type,
        )
        in (
            LearningResourceFeedback
            .objects
            .filter(
                student_profile_id=(
                    student_profile_id
                ),
                learning_resource_id__in=(
                    ids
                ),
            )
            .values_list(
                "learning_resource_id",
                "feedback_type",
            )
        )
    }


@transaction.atomic
def report_learning_resource(
    *,
    student_profile,
    resource_id,
    reason,
    comment="",
):
    """
    Create or reuse one open Student report for the
    same resource and reason.

    A report does not directly change resource health.
    """

    allowed = set(
        LearningResourceReport
        .Reason
        .values
    )

    if reason not in allowed:
        raise ValueError(
            "Invalid Learning Resource report reason."
        )

    resource = (
        _get_available_resource(
            resource_id
        )
    )

    cleaned_comment = str(
        comment
        or ""
    ).strip()

    report = (
        LearningResourceReport
        .objects
        .filter(
            student_profile=(
                student_profile
            ),
            learning_resource=(
                resource
            ),
            reason=reason,
            status=(
                LearningResourceReport
                .Status
                .OPEN
            ),
        )
        .first()
    )

    created = False

    if report is None:
        report = (
            LearningResourceReport
            .objects
            .create(
                student_profile=(
                    student_profile
                ),
                learning_resource=(
                    resource
                ),
                reason=reason,
                comment=(
                    cleaned_comment
                ),
                status=(
                    LearningResourceReport
                    .Status
                    .OPEN
                ),
            )
        )

        created = True

    elif (
        cleaned_comment
        and cleaned_comment
        != report.comment
    ):
        report.comment = (
            cleaned_comment
        )

        report.save(
            update_fields=[
                "comment",
                "updated_at",
            ]
        )

    return (
        LearningResourceReportResult(
            report_id=(
                report.id
            ),
            resource_id=(
                resource.id
            ),
            reason=(
                report.reason
            ),
            status=(
                report.status
            ),
            created=(
                created
            ),
        )
    )
