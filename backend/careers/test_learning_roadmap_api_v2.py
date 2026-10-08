from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import (
    Mock,
    patch,
)

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from careers.models import (
    Career,
    LearningResource,
    LearningResourceSkill,
    RoadmapProgress,
)
from careers.services.learning_resource_discovery import (
    LearningResourceDiscoveryRunResult,
)
from careers.services.learning_roadmap import (
    LearningPlan,
    LearningSuggestion,
    RoadmapStep,
)
from careers.services.readiness_scoring import (
    CareerReadinessResult,
    GapStatus,
    ReadinessStatus,
    SkillGapResult,
)
from profiles.models import (
    Skill,
    StudentProfile,
)


class Sprint3LearningRoadmapAPITests(
    APITestCase
):

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "sprint3-roadmap-api"
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
                name="Software Engineer",
                active=True,
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

        token = str(
            RefreshToken
            .for_user(
                self.user
            )
            .access_token
        )

        self.authorization = (
            f"Bearer {token}"
        )


    def gap(
        self,
    ):
        return SkillGapResult(
            career_skill_id=100,
            skill_id=self.skill.id,
            skill_name=self.skill.name,
            concept_type="skill",
            source_domain=(
                "onet_essential_skills"
            ),
            student_proficiency_level=None,
            student_proficiency_score=(
                Decimal("0")
            ),
            required_level=(
                Decimal("70")
            ),
            importance=(
                Decimal("80")
            ),
            gap_amount=(
                Decimal("70")
            ),
            attainment_ratio=(
                Decimal("0")
            ),
            attainment_percentage=(
                Decimal("0")
            ),
            weighted_contribution=(
                Decimal("0")
            ),
            gap_status=(
                GapStatus.MISSING
            ),
        )


    def plan(
        self,
        *,
        resources=(),
    ):
        gap = self.gap()

        readiness = (
            CareerReadinessResult(
                career_id=self.career.id,
                career_name=(
                    self.career.name
                ),
                score_status=(
                    ReadinessStatus.SCORED
                ),
                readiness_score=(
                    Decimal("40.00")
                ),
                matched_requirement_count=0,
                missing_requirement_count=1,
                below_requirement_count=0,
                meets_requirement_count=0,
                skill_gaps=(
                    gap,
                ),
            )
        )

        suggestion = (
            LearningSuggestion(
                priority=1,
                skill_id=self.skill.id,
                skill_name=self.skill.name,
                gap_status=gap.gap_status,
                current_proficiency=None,
                current_score=(
                    Decimal("0")
                ),
                required_level=(
                    Decimal("70")
                ),
                gap_amount=(
                    Decimal("70")
                ),
                importance=(
                    Decimal("80")
                ),
                resources=tuple(
                    resources
                ),
            )
        )

        roadmap_step = (
            RoadmapStep(
                step_number=1,
                skill_id=self.skill.id,
                skill_name=self.skill.name,
                gap_status=gap.gap_status,
                current_proficiency=None,
                current_score=(
                    Decimal("0")
                ),
                required_level=(
                    Decimal("70")
                ),
                gap_amount=(
                    Decimal("70")
                ),
                importance=(
                    Decimal("80")
                ),
                resources=tuple(
                    resources
                ),
            )
        )

        return LearningPlan(
            student_profile_id=(
                self.profile.id
            ),
            career_id=(
                self.career.id
            ),
            career_name=(
                self.career.name
            ),
            readiness_result=(
                readiness
            ),
            suggestions=(
                suggestion,
            ),
            roadmap_steps=(
                roadmap_step,
            ),
        )


    def create_resource(
        self,
    ):
        resource = (
            LearningResource.objects.create(
                resource_key=(
                    "api-cloud-resource"
                ),
                title=(
                    "Cloud Learning Resource"
                ),
                provider=(
                    "GradNavi Test"
                ),
                url=(
                    "https://example.com/"
                    "api-cloud-resource"
                ),
                resource_type=(
                    LearningResource
                    .ResourceType
                    .COURSE
                ),
                description=(
                    "Cloud deployment learning."
                ),
                access_type=(
                    LearningResource
                    .AccessType
                    .FREE
                ),
                health_status=(
                    LearningResource
                    .HealthStatus
                    .ACTIVE
                ),
                is_active=True,
            )
        )

        LearningResourceSkill.objects.create(
            learning_resource=(
                resource
            ),
            skill=self.skill,
        )

        return resource


    def test_new_endpoints_require_authentication(
        self,
    ):
        response = self.client.get(
            "/api/v1/roadmap-overview/"
            f"?career_id={self.career.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    @patch(
        "careers.views.generate_roadmap_overview"
    )
    @patch(
        "careers.views.resolve_text_model",
        return_value="gpt-test",
    )
    @patch(
        "careers.views.OpenAITextProvider"
    )
    def test_roadmap_overview_returns_progress_and_guidance(
        self,
        provider_class,
        model_mock,
        overview_mock,
    ):
        provider = Mock()

        provider.last_usage = {
            "input_tokens": 1,
            "output_tokens": 1,
            "total_tokens": 2,
        }

        provider.generate.side_effect = (
            Exception(
                "This provider should not be "
                "called in this API shape test."
            )
        )

        provider_class.side_effect = (
            __import__(
                "ai_services.exceptions",
                fromlist=[
                    "AIProviderUnavailableError"
                ],
            )
            .AIProviderUnavailableError(
                "Unavailable"
            )
        )

        overview_mock.return_value = (
            SimpleNamespace(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                score_status="scored",
                readiness_score=(
                    Decimal("40.00")
                ),
                progress_summary=(
                    SimpleNamespace(
                        total=1,
                        completed=0,
                        in_progress=0,
                        not_started=1,
                    )
                ),
                roadmap_steps=(
                    SimpleNamespace(
                        step_number=1,
                        skill_id=(
                            self.skill.id
                        ),
                        skill_name=(
                            self.skill.name
                        ),
                        gap_status="missing",
                        current_proficiency=None,
                        current_score=(
                            Decimal("0")
                        ),
                        required_level=(
                            Decimal("70")
                        ),
                        gap_amount=(
                            Decimal("70")
                        ),
                        importance=(
                            Decimal("80")
                        ),
                        resources=(),
                        progress_status=(
                            "not_started"
                        ),
                        started_at=None,
                        completed_at=None,
                    ),
                ),
            )
        )

        response = self.client.get(
            "/api/v1/roadmap-overview/"
            f"?career_id={self.career.id}",
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "progress_summary"
            ][
                "not_started"
            ],
            1,
        )

        self.assertTrue(
            response.data[
                "data"
            ][
                "guidance"
            ][
                "fallback"
            ]
        )


    @patch(
        "careers.views.generate_learning_plan"
    )
    def test_start_and_complete_progress(
        self,
        plan_mock,
    ):
        plan_mock.return_value = (
            self.plan()
        )

        start = self.client.post(
            "/api/v1/roadmap-progress/start/",
            {
                "career_id": (
                    self.career.id
                ),
                "skill_id": (
                    self.skill.id
                ),
            },
            format="json",
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            start.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            start.data[
                "data"
            ][
                "status"
            ],
            "in_progress",
        )

        complete = self.client.post(
            "/api/v1/roadmap-progress/complete/",
            {
                "career_id": (
                    self.career.id
                ),
                "skill_id": (
                    self.skill.id
                ),
            },
            format="json",
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            complete.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            complete.data[
                "data"
            ][
                "status"
            ],
            "completed",
        )

        self.assertEqual(
            RoadmapProgress
            .objects
            .count(),
            1,
        )


    @patch(
        "careers.views.generate_learning_plan"
    )
    def test_roadmap_student_progress_isolation(
        self,
        plan_mock,
    ):
        from dataclasses import replace

        from ai_services.exceptions import (
            AIProviderUnavailableError,
        )

        student_b = get_user_model().objects.create_user(
            email="sprint4-roadmap-student-b@gradnavi.test",
            password="StrongPassword123!",
        )
        profile_b = StudentProfile.objects.create(
            user=student_b,
        )
        plan = self.plan()

        # Preserve the requested owner in the mocked eligible roadmap.
        def plan_for_student(*, student_profile_id, career_id):
            self.assertEqual(career_id, self.career.id)
            return replace(
                plan,
                student_profile_id=student_profile_id,
            )

        plan_mock.side_effect = plan_for_student
        payload = {
            "career_id": self.career.id,
            "skill_id": self.skill.id,
        }
        start_a = self.client.post(
            "/api/v1/roadmap-progress/start/",
            payload,
            format="json",
            HTTP_AUTHORIZATION=self.authorization,
        )
        self.assertEqual(start_a.status_code, status.HTTP_200_OK)
        self.assertEqual(start_a.data["data"]["status"], "in_progress")
        plan_mock.assert_called_once_with(
            student_profile_id=self.profile.id,
            career_id=self.career.id,
        )
        progress_a = RoadmapProgress.objects.get(
            student_profile=self.profile,
            career=self.career,
            skill=self.skill,
        )
        self.assertEqual(progress_a.status, RoadmapProgress.Status.IN_PROGRESS)
        self.assertIsNotNone(progress_a.started_at)
        self.assertIsNone(progress_a.completed_at)
        original_a = RoadmapProgress.objects.values().get(pk=progress_a.pk)

        token_b = str(RefreshToken.for_user(student_b).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_b}")

        # Use the real overview/progress services; only plan generation
        # and the optional external AI provider are mocked.
        with (
            patch(
                "careers.services.roadmap_overview.generate_learning_plan",
                new=plan_mock,
            ),
            patch("careers.views.resolve_text_model", return_value="gpt-test"),
            patch(
                "careers.views.OpenAITextProvider",
                side_effect=AIProviderUnavailableError("Unavailable"),
            ),
        ):
            plan_mock.reset_mock()
            overview_b = self.client.get(
                "/api/v1/roadmap-overview/",
                {"career_id": self.career.id},
            )
            self.assertEqual(overview_b.status_code, status.HTTP_200_OK)
            step_b = overview_b.data["data"]["roadmap_steps"][0]
            self.assertEqual(step_b["skill_id"], self.skill.id)
            self.assertEqual(step_b["progress_status"], "not_started")
            self.assertIsNone(step_b["started_at"])
            self.assertIsNone(step_b["completed_at"])
            self.assertEqual(
                overview_b.data["data"]["progress_summary"],
                {"total": 1, "completed": 0, "in_progress": 0, "not_started": 1},
            )
            plan_mock.assert_called_once_with(
                student_profile_id=profile_b.id,
                career_id=self.career.id,
            )
            self.assertEqual(
                RoadmapProgress.objects.values().get(pk=progress_a.pk),
                original_a,
            )
            self.assertFalse(
                RoadmapProgress.objects.filter(student_profile=profile_b).exists()
            )

            # The same public career/skill identifiers must affect only B.
            for operation, expected_status in (
                ("start", "in_progress"),
                ("complete", "completed"),
            ):
                with self.subTest(operation=operation):
                    plan_mock.reset_mock()
                    response_b = self.client.post(
                        f"/api/v1/roadmap-progress/{operation}/",
                        payload,
                        format="json",
                    )
                    self.assertEqual(response_b.status_code, status.HTTP_200_OK)
                    self.assertEqual(
                        response_b.data["data"]["status"], expected_status
                    )
                    plan_mock.assert_called_once_with(
                        student_profile_id=profile_b.id,
                        career_id=self.career.id,
                    )
                    progress_b = RoadmapProgress.objects.get(
                        student_profile=profile_b,
                        career=self.career,
                        skill=self.skill,
                    )
                    self.assertNotEqual(progress_b.pk, progress_a.pk)
                    self.assertEqual(progress_b.student_profile_id, profile_b.id)
                    self.assertEqual(progress_b.student_profile.user_id, student_b.id)
                    self.assertEqual(progress_b.status, expected_status)
                    self.assertEqual(RoadmapProgress.objects.count(), 2)
                    self.assertEqual(
                        RoadmapProgress.objects.values().get(pk=progress_a.pk),
                        original_a,
                    )

            plan_mock.reset_mock()
            overview_b = self.client.get(
                "/api/v1/roadmap-overview/",
                {"career_id": self.career.id},
            )
            self.assertEqual(overview_b.status_code, status.HTTP_200_OK)
            self.assertEqual(
                overview_b.data["data"]["roadmap_steps"][0]["progress_status"],
                "completed",
            )
            self.assertEqual(
                overview_b.data["data"]["progress_summary"],
                {"total": 1, "completed": 1, "in_progress": 0, "not_started": 0},
            )
            plan_mock.assert_called_once_with(
                student_profile_id=profile_b.id,
                career_id=self.career.id,
            )
            self.assertEqual(
                RoadmapProgress.objects.values().get(pk=progress_a.pk),
                original_a,
            )

        progress_a.refresh_from_db()
        self.assertEqual(progress_a.student_profile_id, self.profile.id)
        self.assertEqual(progress_a.student_profile.user_id, self.user.id)
        self.assertEqual(progress_a.status, RoadmapProgress.Status.IN_PROGRESS)


    @patch(
        "careers.views.ensure_learning_resource_catalogue"
    )
    @patch(
        "careers.views.generate_learning_plan"
    )
    @patch(
        "careers.views.resolve_text_model",
        return_value="gpt-test",
    )
    @patch(
        "careers.views.OpenAITextProvider"
    )
    def test_learning_resource_recommendations_return_ranked_resources(
        self,
        provider_class,
        model_mock,
        plan_mock,
        discovery_mock,
    ):
        resource = (
            self.create_resource()
        )

        discovery_mock.return_value = (
            LearningResourceDiscoveryRunResult(
                attempted=False,
                reason="cooldown",
                status="partial",
                resource_count_before=1,
                resource_count_after=1,
                requested_count=0,
                candidate_count=0,
                persisted_count=0,
                next_eligible_at=None,
            )
        )

        plan_mock.return_value = (
            self.plan()
        )

        provider_class.side_effect = (
            __import__(
                "ai_services.exceptions",
                fromlist=[
                    "AIProviderUnavailableError"
                ],
            )
            .AIProviderUnavailableError(
                "Unavailable"
            )
        )

        response = self.client.get(
            (
                "/api/v1/"
                "learning-resource-recommendations/"
                f"?career_id={self.career.id}"
                f"&skill_id={self.skill.id}"
            ),
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        discovery_mock.assert_called_once_with(
            skill_id=(
                self.skill.id
            ),
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "discovery"
            ][
                "reason"
            ],
            "cooldown",
        )

        self.assertFalse(
            response.data[
                "data"
            ][
                "discovery"
            ][
                "attempted"
            ]
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "resource_count"
            ],
            1,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "resources"
            ][0][
                "id"
            ],
            resource.id,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "resources"
            ][0][
                "explanation_source"
            ],
            "deterministic",
        )


    @patch(
        "careers.views.get_or_generate_learning_resource_guidance"
    )
    @patch(
        "careers.views.load_ranked_learning_resources"
    )
    @patch(
        "careers.views.ensure_learning_resource_catalogue"
    )
    @patch(
        "careers.views.generate_learning_plan"
    )
    def test_learning_resource_api_runs_discovery_before_ranking(
        self,
        plan_mock,
        discovery_mock,
        ranking_mock,
        guidance_mock,
    ):
        plan_mock.return_value = (
            self.plan()
        )

        call_order = []

        def discovery_side_effect(
            *,
            skill_id,
        ):
            call_order.append(
                "discovery"
            )

            return (
                LearningResourceDiscoveryRunResult(
                    attempted=True,
                    reason="completed",
                    status="success",
                    resource_count_before=0,
                    resource_count_after=6,
                    requested_count=6,
                    candidate_count=6,
                    persisted_count=6,
                    next_eligible_at=None,
                )
            )

        def ranking_side_effect(
            **kwargs,
        ):
            call_order.append(
                "ranking"
            )

            return ()

        discovery_mock.side_effect = (
            discovery_side_effect
        )

        ranking_mock.side_effect = (
            ranking_side_effect
        )

        guidance_mock.return_value = {
            "guidance_items": [],
            "is_ai_generated": False,
            "fallback": True,
            "cached": False,
            "model": "gpt-test",
            "version": "test",
        }

        response = self.client.get(
            (
                "/api/v1/"
                "learning-resource-recommendations/"
                f"?career_id={self.career.id}"
                f"&skill_id={self.skill.id}"
            ),
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            call_order,
            [
                "discovery",
                "ranking",
            ],
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "discovery"
            ][
                "persisted_count"
            ],
            6,
        )


    @patch(
        "careers.views.ensure_learning_resource_catalogue"
    )
    @patch(
        "careers.views.generate_learning_plan"
    )
    @patch(
        "careers.views.resolve_text_model",
        return_value="gpt-test",
    )
    @patch(
        "careers.views.OpenAITextProvider"
    )
    def test_learning_resource_access_filter_does_not_change_discovery_scope(
        self,
        provider_class,
        model_mock,
        plan_mock,
        discovery_mock,
    ):
        free_resource = (
            self.create_resource()
        )

        plan_mock.return_value = (
            self.plan()
        )

        discovery_mock.return_value = (
            LearningResourceDiscoveryRunResult(
                attempted=False,
                reason="enough_resources",
                status=None,
                resource_count_before=6,
                resource_count_after=6,
                requested_count=0,
                candidate_count=0,
                persisted_count=0,
                next_eligible_at=None,
            )
        )

        provider_class.side_effect = (
            __import__(
                "ai_services.exceptions",
                fromlist=[
                    "AIProviderUnavailableError"
                ],
            )
            .AIProviderUnavailableError(
                "Unavailable"
            )
        )

        response = self.client.get(
            (
                "/api/v1/"
                "learning-resource-recommendations/"
                f"?career_id={self.career.id}"
                f"&skill_id={self.skill.id}"
                "&access_type=free"
            ),
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        discovery_mock.assert_called_once_with(
            skill_id=(
                self.skill.id
            ),
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "resources"
            ][0][
                "id"
            ],
            free_resource.id,
        )


    @patch(
        "careers.views.ensure_learning_resource_catalogue"
    )
    @patch(
        "careers.views.generate_learning_plan"
    )
    @patch(
        "careers.views.resolve_text_model",
        return_value="gpt-test",
    )
    @patch(
        "careers.views.OpenAITextProvider"
    )
    def test_learning_resource_discovery_failure_keeps_existing_resources_available(
        self,
        provider_class,
        model_mock,
        plan_mock,
        discovery_mock,
    ):
        resource = (
            self.create_resource()
        )

        plan_mock.return_value = (
            self.plan()
        )

        discovery_mock.return_value = (
            LearningResourceDiscoveryRunResult(
                attempted=True,
                reason="provider_failure",
                status="provider_failure",
                resource_count_before=1,
                resource_count_after=1,
                requested_count=5,
                candidate_count=0,
                persisted_count=0,
                next_eligible_at=None,
            )
        )

        provider_class.side_effect = (
            __import__(
                "ai_services.exceptions",
                fromlist=[
                    "AIProviderUnavailableError"
                ],
            )
            .AIProviderUnavailableError(
                "Unavailable"
            )
        )

        response = self.client.get(
            (
                "/api/v1/"
                "learning-resource-recommendations/"
                f"?career_id={self.career.id}"
                f"&skill_id={self.skill.id}"
            ),
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "discovery"
            ][
                "reason"
            ],
            "provider_failure",
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "resource_count"
            ],
            1,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "resources"
            ][0][
                "id"
            ],
            resource.id,
        )


    def test_feedback_endpoint_updates_current_vote(
        self,
    ):
        resource = (
            self.create_resource()
        )

        first = self.client.put(
            (
                "/api/v1/"
                "learning-resource-feedback/"
                f"{resource.id}/"
            ),
            {
                "feedback_type": (
                    "helpful"
                ),
            },
            format="json",
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            first.status_code,
            status.HTTP_200_OK,
        )

        second = self.client.put(
            (
                "/api/v1/"
                "learning-resource-feedback/"
                f"{resource.id}/"
            ),
            {
                "feedback_type": (
                    "not_helpful"
                ),
            },
            format="json",
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            second.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            second.data[
                "data"
            ][
                "feedback_type"
            ],
            "not_helpful",
        )

        self.assertEqual(
            second.data[
                "data"
            ][
                "not_helpful_count"
            ],
            1,
        )


    def test_report_endpoint_creates_review_record(
        self,
    ):
        resource = (
            self.create_resource()
        )

        response = self.client.post(
            "/api/v1/learning-resource-reports/",
            {
                "resource_id": (
                    resource.id
                ),
                "reason": (
                    "broken_link"
                ),
                "comment": (
                    "The page did not load."
                ),
            },
            format="json",
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "status"
            ],
            "open",
        )

        resource.refresh_from_db()

        self.assertEqual(
            resource.health_status,
            (
                LearningResource
                .HealthStatus
                .ACTIVE
            ),
        )


    def test_original_wbs57_routes_still_resolve(
        self,
    ):
        from django.urls import resolve

        self.assertEqual(
            resolve(
                "/api/v1/roadmaps/"
            ).url_name,
            "roadmap-list",
        )

        self.assertEqual(
            resolve(
                "/api/v1/learning-resources/"
            ).url_name,
            "learning-resource-suggestions",
        )
