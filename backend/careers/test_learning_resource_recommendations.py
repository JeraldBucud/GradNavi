from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from careers.models import (
    LearningResource,
    LearningResourceFeedback,
    LearningResourceSkill,
)
from careers.services.learning_resource_recommendations import (
    MAX_RESOURCES_PER_SKILL,
    build_why_this_fits,
    load_ranked_learning_resources,
)
from profiles.models import (
    Skill,
    StudentProfile,
)


class LearningResourceRecommendationServiceTests(
    TestCase
):

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "resource-ranking"
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

        self.skill = (
            Skill.objects.create(
                name="Cloud Deployment",
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )


    def make_profile(
        self,
        number,
    ):
        user_model = get_user_model()

        user = (
            user_model.objects.create_user(
                email=(
                    f"resource-feedback-{number}"
                    "@gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        return (
            StudentProfile.objects.create(
                user=user,
            )
        )


    def make_resource(
        self,
        *,
        key,
        title,
        access_type=(
            LearningResource
            .AccessType
            .UNKNOWN
        ),
        health_status=(
            LearningResource
            .HealthStatus
            .ACTIVE
        ),
        is_active=True,
        verified=False,
    ):
        resource = (
            LearningResource.objects.create(
                resource_key=key,
                title=title,
                provider=(
                    "GradNavi Test Provider"
                ),
                url=(
                    "https://example.com/"
                    + key
                ),
                resource_type=(
                    LearningResource
                    .ResourceType
                    .COURSE
                ),
                description=(
                    "Controlled test resource."
                ),
                access_type=access_type,
                health_status=(
                    health_status
                ),
                is_active=is_active,
                last_verified_at=(
                    timezone.now()
                    if verified
                    else None
                ),
            )
        )

        LearningResourceSkill.objects.create(
            learning_resource=resource,
            skill=self.skill,
        )

        return resource


    def add_feedback(
        self,
        *,
        resource,
        feedback_type,
        number,
    ):
        LearningResourceFeedback.objects.create(
            student_profile=(
                self.make_profile(
                    number
                )
            ),
            learning_resource=resource,
            feedback_type=(
                feedback_type
            ),
        )


    def test_only_active_healthy_resources_are_returned(
        self,
    ):
        eligible = self.make_resource(
            key="eligible",
            title="Eligible",
        )

        self.make_resource(
            key="inactive",
            title="Inactive",
            is_active=False,
        )

        self.make_resource(
            key="needs-review",
            title="Needs Review",
            health_status=(
                LearningResource
                .HealthStatus
                .NEEDS_REVIEW
            ),
        )

        self.make_resource(
            key="broken",
            title="Broken",
            health_status=(
                LearningResource
                .HealthStatus
                .BROKEN
            ),
        )

        self.make_resource(
            key="archived",
            title="Archived",
            health_status=(
                LearningResource
                .HealthStatus
                .ARCHIVED
            ),
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            [
                item.id
                for item
                in result
            ],
            [
                eligible.id,
            ],
        )


    def test_unknown_access_remains_eligible(
        self,
    ):
        resource = self.make_resource(
            key="unknown",
            title="Unknown Access",
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            result[0].id,
            resource.id,
        )

        self.assertEqual(
            result[0].access_type,
            (
                LearningResource
                .AccessType
                .UNKNOWN
            ),
        )


    def test_helpful_feedback_improves_ranking(
        self,
    ):
        neutral = self.make_resource(
            key="neutral-helpful",
            title="Neutral",
        )

        helpful = self.make_resource(
            key="helpful",
            title="Helpful",
        )

        self.add_feedback(
            resource=helpful,
            feedback_type=(
                LearningResourceFeedback
                .FeedbackType
                .HELPFUL
            ),
            number=1,
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            result[0].id,
            helpful.id,
        )

        self.assertEqual(
            result[1].id,
            neutral.id,
        )


    def test_not_helpful_feedback_lowers_ranking(
        self,
    ):
        neutral = self.make_resource(
            key="neutral-negative",
            title="Neutral",
        )

        negative = self.make_resource(
            key="negative",
            title="Negative",
        )

        self.add_feedback(
            resource=negative,
            feedback_type=(
                LearningResourceFeedback
                .FeedbackType
                .NOT_HELPFUL
            ),
            number=2,
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            result[0].id,
            neutral.id,
        )

        self.assertEqual(
            result[1].id,
            negative.id,
        )


    def test_verified_resource_breaks_equal_feedback_tie(
        self,
    ):
        unchecked = self.make_resource(
            key="unchecked",
            title="A Unchecked",
        )

        verified = self.make_resource(
            key="verified",
            title="Z Verified",
            verified=True,
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            result[0].id,
            verified.id,
        )

        self.assertEqual(
            result[1].id,
            unchecked.id,
        )


    def test_access_type_breaks_equal_quality_tie(
        self,
    ):
        unknown = self.make_resource(
            key="unknown-access",
            title="A Unknown",
            access_type=(
                LearningResource
                .AccessType
                .UNKNOWN
            ),
        )

        paid = self.make_resource(
            key="paid",
            title="B Paid",
            access_type=(
                LearningResource
                .AccessType
                .PAID
            ),
        )

        freemium = self.make_resource(
            key="freemium",
            title="C Freemium",
            access_type=(
                LearningResource
                .AccessType
                .FREEMIUM
            ),
        )

        free = self.make_resource(
            key="free",
            title="D Free",
            access_type=(
                LearningResource
                .AccessType
                .FREE
            ),
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            [
                item.id
                for item
                in result
            ],
            [
                free.id,
                freemium.id,
                paid.id,
                unknown.id,
            ],
        )


    def test_access_filter_works(
        self,
    ):
        free = self.make_resource(
            key="filter-free",
            title="Filter Free",
            access_type=(
                LearningResource
                .AccessType
                .FREE
            ),
        )

        self.make_resource(
            key="filter-paid",
            title="Filter Paid",
            access_type=(
                LearningResource
                .AccessType
                .PAID
            ),
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
                access_types=(
                    LearningResource
                    .AccessType
                    .FREE,
                ),
            )
        )

        self.assertEqual(
            [
                item.id
                for item
                in result
            ],
            [
                free.id,
            ],
        )


    def test_maximum_is_twelve(
        self,
    ):
        for index in range(
            15
        ):
            self.make_resource(
                key=(
                    f"limit-{index:02d}"
                ),
                title=(
                    f"Resource {index:02d}"
                ),
            )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
                limit=50,
            )
        )

        self.assertEqual(
            len(
                result
            ),
            MAX_RESOURCES_PER_SKILL,
        )

        self.assertEqual(
            MAX_RESOURCES_PER_SKILL,
            12,
        )


    def test_no_minimum_is_forced(
        self,
    ):
        self.make_resource(
            key="only-one",
            title="Only One",
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            len(
                result
            ),
            1,
        )


    def test_fit_text_is_grounded(
        self,
    ):
        resource = self.make_resource(
            key="fit",
            title="Fit",
            access_type=(
                LearningResource
                .AccessType
                .FREE
            ),
        )

        text = build_why_this_fits(
            resource=resource,
            skill_name=(
                "Cloud Deployment"
            ),
            career_name=(
                "Software Engineer"
            ),
        )

        self.assertEqual(
            text,
            (
                "Free course matched to your "
                "Cloud Deployment skill gap "
                "for Software Engineer."
            ),
        )


    def test_feedback_counts_are_returned(
        self,
    ):
        resource = self.make_resource(
            key="feedback-counts",
            title="Feedback Counts",
        )

        self.add_feedback(
            resource=resource,
            feedback_type=(
                LearningResourceFeedback
                .FeedbackType
                .HELPFUL
            ),
            number=10,
        )

        self.add_feedback(
            resource=resource,
            feedback_type=(
                LearningResourceFeedback
                .FeedbackType
                .HELPFUL
            ),
            number=11,
        )

        self.add_feedback(
            resource=resource,
            feedback_type=(
                LearningResourceFeedback
                .FeedbackType
                .NOT_HELPFUL
            ),
            number=12,
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            result[0].helpful_count,
            2,
        )

        self.assertEqual(
            result[0].not_helpful_count,
            1,
        )

        self.assertEqual(
            result[0].feedback_score,
            1,
        )


    def test_reports_do_not_directly_change_ranking_health(
        self,
    ):
        resource = self.make_resource(
            key="report-independent",
            title="Report Independent",
        )

        result = (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
            )
        )

        self.assertEqual(
            [
                item.id
                for item
                in result
            ],
            [
                resource.id,
            ],
        )
