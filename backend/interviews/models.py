from django.conf import settings
from django.db import models
from django.db.models import F, Q


class InterviewSession(models.Model):
    """
    Minimal completed Interview Preparation history.

    FR-13 stores metadata only.

    Typed answers, generated feedback, and job descriptions
    are intentionally excluded from persistence.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interview_sessions",
    )

    target_role = models.CharField(
        max_length=255,
    )

    total_questions = models.PositiveSmallIntegerField()

    questions_with_feedback = models.PositiveSmallIntegerField(
        default=0,
    )

    completed_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = (
            "-completed_at",
            "-id",
        )

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(total_questions__gte=1)
                    & Q(total_questions__lte=10)
                ),
                name=(
                    "interview_session_total_questions_1_10"
                ),
            ),
            models.CheckConstraint(
                condition=(
                    Q(questions_with_feedback__gte=0)
                    & Q(
                        questions_with_feedback__lte=F(
                            "total_questions"
                        )
                    )
                ),
                name=(
                    "interview_session_feedback_lte_total"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} - "
            f"{self.target_role} - "
            f"{self.completed_at}"
        )
