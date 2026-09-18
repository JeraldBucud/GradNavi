from django.contrib.auth import get_user_model
from django.db import (
    IntegrityError,
    transaction,
)
from django.test import TestCase

from careers.models import (
    Career,
    LearningResource,
    LearningResourceFeedback,
    LearningResourceReport,
    RoadmapGuidanceSnapshot,
    RoadmapProgress,
)
from profiles.models import (
    Skill,
    StudentProfile,
)


class LearningRoadmapFoundationModelTests(
    TestCase
):
    """
    Sprint 3 database-foundation tests for Career Roadmap
    and Learning Resources enhancements.
    """

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "roadmap-foundation"
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

        self.career = (
            Career.objects.create(
                name=(
                    "Roadmap Foundation Career"
                ),
                active=True,
            )
        )

        self.skill = Skill.objects.create(
            name="Roadmap Foundation Skill",
            concept_type=(
                Skill.ConceptType.SKILL
            ),
        )

        self.resource = (
            LearningResource.objects.create(
                resource_key=(
                    "roadmap_foundation_resource"
                ),
                title=(
                    "Roadmap Foundation Resource"
                ),
                provider=(
                    "GradNavi Test"
                ),
                url=(
                    "https://example.com/"
                    "roadmap-foundation-resource"
                ),
                resource_type=(
                    LearningResource
                    .ResourceType
                    .COURSE
                ),
            )
        )


    def test_learning_resource_safe_defaults(
        self,
    ):
        self.assertEqual(
            self.resource.access_type,
            (
                LearningResource
                .AccessType
                .UNKNOWN
            ),
        )

        self.assertEqual(
            self.resource.source_type,
            (
                LearningResource
                .SourceType
                .CURATED
            ),
        )

        self.assertEqual(
            self.resource.health_status,
            (
                LearningResource
                .HealthStatus
                .ACTIVE
            ),
        )

        self.assertIsNone(
            self.resource.last_checked_at
        )

        self.assertIsNone(
            self.resource.last_verified_at
        )


    def test_learning_resource_supports_access_types(
        self,
    ):
        expected_values = {
            "free",
            "freemium",
            "paid",
            "unknown",
        }

        actual_values = {
            value
            for value, _
            in (
                LearningResource
                .AccessType
                .choices
            )
        }

        self.assertEqual(
            actual_values,
            expected_values,
        )


    def test_roadmap_progress_defaults_to_not_started(
        self,
    ):
        progress = (
            RoadmapProgress.objects.create(
                student_profile=self.profile,
                career=self.career,
                skill=self.skill,
            )
        )

        self.assertEqual(
            progress.status,
            (
                RoadmapProgress
                .Status
                .NOT_STARTED
            ),
        )

        self.assertIsNone(
            progress.started_at
        )

        self.assertIsNone(
            progress.completed_at
        )


    def test_roadmap_progress_is_unique_per_student_career_skill(
        self,
    ):
        RoadmapProgress.objects.create(
            student_profile=self.profile,
            career=self.career,
            skill=self.skill,
        )

        with (
            self.assertRaises(
                IntegrityError
            ),
            transaction.atomic(),
        ):
            RoadmapProgress.objects.create(
                student_profile=self.profile,
                career=self.career,
                skill=self.skill,
            )


    def test_learning_resource_feedback_is_one_current_vote_per_student_resource(
        self,
    ):
        LearningResourceFeedback.objects.create(
            student_profile=self.profile,
            learning_resource=self.resource,
            feedback_type=(
                LearningResourceFeedback
                .FeedbackType
                .HELPFUL
            ),
        )

        with (
            self.assertRaises(
                IntegrityError
            ),
            transaction.atomic(),
        ):
            LearningResourceFeedback.objects.create(
                student_profile=self.profile,
                learning_resource=self.resource,
                feedback_type=(
                    LearningResourceFeedback
                    .FeedbackType
                    .NOT_HELPFUL
                ),
            )


    def test_learning_resource_report_defaults_to_open(
        self,
    ):
        report = (
            LearningResourceReport
            .objects
            .create(
                student_profile=self.profile,
                learning_resource=self.resource,
                reason=(
                    LearningResourceReport
                    .Reason
                    .BROKEN_LINK
                ),
            )
        )

        self.assertEqual(
            report.status,
            (
                LearningResourceReport
                .Status
                .OPEN
            ),
        )


    def test_report_reason_catalogue_matches_product_decision(
        self,
    ):
        expected_values = {
            "broken_link",
            "outdated",
            "not_relevant",
            "too_difficult",
            "requires_payment",
            "duplicate",
            "other",
        }

        actual_values = {
            value
            for value, _
            in (
                LearningResourceReport
                .Reason
                .choices
            )
        }

        self.assertEqual(
            actual_values,
            expected_values,
        )


    def test_one_guidance_snapshot_per_student_and_career(
        self,
    ):
        RoadmapGuidanceSnapshot.objects.create(
            student_profile=self.profile,
            career=self.career,
            cache_key="a" * 64,
            guidance_version=(
                "roadmap_guidance_v1"
            ),
            model="test-model",
            payload={
                "steps": [],
            },
        )

        with (
            self.assertRaises(
                IntegrityError
            ),
            transaction.atomic(),
        ):
            RoadmapGuidanceSnapshot.objects.create(
                student_profile=self.profile,
                career=self.career,
                cache_key="b" * 64,
                guidance_version=(
                    "roadmap_guidance_v1"
                ),
                model="test-model",
                payload={
                    "steps": [],
                },
            )
