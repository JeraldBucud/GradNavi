from django.contrib.auth import get_user_model
from django.test import TestCase

from careers.models import (
    LearningResource,
    LearningResourceFeedback,
    LearningResourceReport,
)
from careers.services.learning_resource_interactions import (
    report_learning_resource,
    set_learning_resource_feedback,
)
from profiles.models import (
    StudentProfile,
)


class LearningResourceInteractionServiceTests(
    TestCase
):

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "resource-interactions"
                    "@gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        self.profile = (
            StudentProfile.objects.create(
                user=self.user,
            )
        )

        self.resource = (
            LearningResource.objects.create(
                resource_key=(
                    "interaction-resource"
                ),
                title=(
                    "Interaction Resource"
                ),
                provider=(
                    "GradNavi Test"
                ),
                url=(
                    "https://example.com/"
                    "interaction-resource"
                ),
                resource_type=(
                    LearningResource
                    .ResourceType
                    .COURSE
                ),
                health_status=(
                    LearningResource
                    .HealthStatus
                    .ACTIVE
                ),
                is_active=True,
            )
        )


    def test_feedback_is_created(
        self,
    ):
        result = (
            set_learning_resource_feedback(
                student_profile=(
                    self.profile
                ),
                resource_id=(
                    self.resource.id
                ),
                feedback_type=(
                    LearningResourceFeedback
                    .FeedbackType
                    .HELPFUL
                ),
            )
        )

        self.assertEqual(
            result.feedback_type,
            "helpful",
        )

        self.assertEqual(
            result.helpful_count,
            1,
        )


    def test_feedback_changes_without_duplicate_vote(
        self,
    ):
        set_learning_resource_feedback(
            student_profile=self.profile,
            resource_id=self.resource.id,
            feedback_type="helpful",
        )

        result = (
            set_learning_resource_feedback(
                student_profile=(
                    self.profile
                ),
                resource_id=(
                    self.resource.id
                ),
                feedback_type=(
                    "not_helpful"
                ),
            )
        )

        self.assertEqual(
            LearningResourceFeedback
            .objects
            .count(),
            1,
        )

        self.assertEqual(
            result.helpful_count,
            0,
        )

        self.assertEqual(
            result.not_helpful_count,
            1,
        )


    def test_report_does_not_change_resource_health(
        self,
    ):
        result = (
            report_learning_resource(
                student_profile=(
                    self.profile
                ),
                resource_id=(
                    self.resource.id
                ),
                reason=(
                    LearningResourceReport
                    .Reason
                    .BROKEN_LINK
                ),
                comment=(
                    "The page did not load."
                ),
            )
        )

        self.resource.refresh_from_db()

        self.assertTrue(
            result.created
        )

        self.assertEqual(
            self.resource.health_status,
            (
                LearningResource
                .HealthStatus
                .ACTIVE
            ),
        )


    def test_duplicate_open_report_is_reused(
        self,
    ):
        first = (
            report_learning_resource(
                student_profile=(
                    self.profile
                ),
                resource_id=(
                    self.resource.id
                ),
                reason="outdated",
            )
        )

        second = (
            report_learning_resource(
                student_profile=(
                    self.profile
                ),
                resource_id=(
                    self.resource.id
                ),
                reason="outdated",
            )
        )

        self.assertTrue(
            first.created
        )

        self.assertFalse(
            second.created
        )

        self.assertEqual(
            first.report_id,
            second.report_id,
        )

        self.assertEqual(
            LearningResourceReport
            .objects
            .count(),
            1,
        )
