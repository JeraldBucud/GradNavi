from django.contrib.auth import (
    get_user_model,
)
from rest_framework import status
from rest_framework.test import (
    APITestCase,
)
from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from careers.models import Career
from profiles.models import (
    CareerGoal,
    StudentProfile,
)


User = get_user_model()


class StructuredCareerGoalAPITests(
    APITestCase
):
    def setUp(self):
        self.url = (
            "/api/v1/profile/"
        )

        self.user = (
            User.objects.create_user(
                email=(
                    "career-goal-api"
                    "@gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        self.other_user = (
            User.objects.create_user(
                email=(
                    "career-goal-other"
                    "@gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        self.profile = (
            StudentProfile.objects.create(
                user=self.user
            )
        )

        self.other_profile = (
            StudentProfile.objects.create(
                user=self.other_user
            )
        )

        self.access_token = str(
            RefreshToken.for_user(
                self.user
            ).access_token
        )

        self.software = (
            Career.objects.create(
                name="Software Engineer",
                category="Technology",
                active=True,
            )
        )

        self.data = (
            Career.objects.create(
                name="Data Scientist",
                category="Data",
                active=True,
            )
        )

        self.cloud = (
            Career.objects.create(
                name="Cloud Engineer",
                category="Technology",
                active=True,
            )
        )

        self.inactive = (
            Career.objects.create(
                name="Inactive Career",
                category="Legacy",
                active=False,
            )
        )

    def patch_profile(
        self,
        career_goals,
    ):
        return self.client.patch(
            self.url,
            {
                "career_goals": (
                    career_goals
                )
            },
            format="json",
            HTTP_AUTHORIZATION=(
                "Bearer "
                f"{self.access_token}"
            ),
        )

    def test_structured_career_id_creates_goal(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "career_id": (
                        self.software.id
                    ),
                    "description": (
                        "Backend development."
                    ),
                    "is_primary": True,
                }
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        goal = (
            self.profile
            .career_goals
            .get()
        )

        self.assertEqual(
            goal.career,
            self.software,
        )

        self.assertEqual(
            goal.target_role,
            "Software Engineer",
        )

        self.assertTrue(
            goal.is_primary
        )

        result = (
            response.data[
                "data"
            ][
                "profile"
            ][
                "career_goals"
            ][0]
        )

        self.assertEqual(
            result[
                "career_id"
            ],
            self.software.id,
        )

        self.assertEqual(
            result[
                "target_role"
            ],
            "Software Engineer",
        )

        self.assertTrue(
            result[
                "is_primary"
            ]
        )

    def test_single_goal_becomes_primary_automatically(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "career_id": (
                        self.data.id
                    )
                }
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            self.profile
            .career_goals
            .get()
            .is_primary
        )

    def test_multiple_goals_support_one_primary(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "career_id": (
                        self.software.id
                    ),
                    "is_primary": True,
                },
                {
                    "career_id": (
                        self.data.id
                    ),
                    "is_primary": False,
                },
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            self.profile
            .career_goals
            .filter(
                is_primary=True
            )
            .count(),
            1,
        )

    def test_multiple_goals_without_primary_select_first(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "career_id": (
                        self.software.id
                    ),
                },
                {
                    "career_id": (
                        self.data.id
                    ),
                },
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        primary = (
            self.profile
            .career_goals
            .get(
                is_primary=True
            )
        )

        self.assertEqual(
            primary.career,
            self.software,
        )

    def test_duplicate_career_is_rejected(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "career_id": (
                        self.software.id
                    ),
                },
                {
                    "career_id": (
                        self.software.id
                    ),
                },
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            self.profile
            .career_goals
            .exists()
        )

    def test_multiple_primary_goals_are_rejected(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "career_id": (
                        self.software.id
                    ),
                    "is_primary": True,
                },
                {
                    "career_id": (
                        self.data.id
                    ),
                    "is_primary": True,
                },
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            self.profile
            .career_goals
            .exists()
        )

    def test_inactive_career_id_is_rejected(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "career_id": (
                        self.inactive.id
                    )
                }
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            self.profile
            .career_goals
            .exists()
        )

    def test_missing_career_reference_is_rejected_for_new_goal(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "description": (
                        "Missing Career."
                    )
                }
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_mismatched_career_id_and_target_role_are_rejected(
        self,
    ):
        response = self.patch_profile(
            [
                {
                    "career_id": (
                        self.software.id
                    ),
                    "target_role": (
                        "Data Scientist"
                    ),
                }
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_legacy_matching_target_role_links_career(
        self,
    ):
        response = self.patch_profile(
            [
                "Software Engineer"
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        goal = (
            self.profile
            .career_goals
            .get()
        )

        self.assertEqual(
            goal.career,
            self.software,
        )

        self.assertEqual(
            goal.target_role,
            self.software.name,
        )

    def test_legacy_unmatched_target_role_stays_supported(
        self,
    ):
        response = self.patch_profile(
            [
                "Legacy Custom Role"
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        goal = (
            self.profile
            .career_goals
            .get()
        )

        self.assertIsNone(
            goal.career
        )

        self.assertEqual(
            goal.target_role,
            "Legacy Custom Role",
        )

        self.assertTrue(
            goal.is_primary
        )

    def test_existing_goal_updates_to_new_career_and_syncs_target_role(
        self,
    ):
        goal = (
            CareerGoal.objects.create(
                student_profile=(
                    self.profile
                ),
                career=self.software,
                target_role=(
                    self.software.name
                ),
                is_primary=True,
            )
        )

        response = self.patch_profile(
            [
                {
                    "id": goal.id,
                    "career_id": (
                        self.data.id
                    ),
                    "description": (
                        "Updated target."
                    ),
                    "is_primary": True,
                }
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        goal.refresh_from_db()

        self.assertEqual(
            goal.career,
            self.data,
        )

        self.assertEqual(
            goal.target_role,
            self.data.name,
        )

        self.assertEqual(
            goal.description,
            "Updated target.",
        )

    def test_description_only_update_preserves_structured_career(
        self,
    ):
        goal = (
            CareerGoal.objects.create(
                student_profile=(
                    self.profile
                ),
                career=self.software,
                target_role=(
                    self.software.name
                ),
                description="Old",
                is_primary=True,
            )
        )

        response = self.patch_profile(
            [
                {
                    "id": goal.id,
                    "description": "New",
                }
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        goal.refresh_from_db()

        self.assertEqual(
            goal.career,
            self.software,
        )

        self.assertEqual(
            goal.target_role,
            self.software.name,
        )

        self.assertEqual(
            goal.description,
            "New",
        )

        self.assertTrue(
            goal.is_primary
        )

    def test_primary_goal_switch_is_safe(
        self,
    ):
        first = (
            CareerGoal.objects.create(
                student_profile=(
                    self.profile
                ),
                career=self.software,
                target_role=(
                    self.software.name
                ),
                is_primary=True,
            )
        )

        second = (
            CareerGoal.objects.create(
                student_profile=(
                    self.profile
                ),
                career=self.data,
                target_role=(
                    self.data.name
                ),
                is_primary=False,
            )
        )

        response = self.patch_profile(
            [
                {
                    "id": first.id,
                    "career_id": (
                        self.software.id
                    ),
                    "is_primary": False,
                },
                {
                    "id": second.id,
                    "career_id": (
                        self.data.id
                    ),
                    "is_primary": True,
                },
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        first.refresh_from_db()
        second.refresh_from_db()

        self.assertFalse(
            first.is_primary
        )

        self.assertTrue(
            second.is_primary
        )

    def test_career_swap_between_existing_goals_is_safe(
        self,
    ):
        first = (
            CareerGoal.objects.create(
                student_profile=(
                    self.profile
                ),
                career=self.software,
                target_role=(
                    self.software.name
                ),
                is_primary=True,
            )
        )

        second = (
            CareerGoal.objects.create(
                student_profile=(
                    self.profile
                ),
                career=self.data,
                target_role=(
                    self.data.name
                ),
                is_primary=False,
            )
        )

        response = self.patch_profile(
            [
                {
                    "id": first.id,
                    "career_id": (
                        self.data.id
                    ),
                    "is_primary": True,
                },
                {
                    "id": second.id,
                    "career_id": (
                        self.software.id
                    ),
                    "is_primary": False,
                },
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        first.refresh_from_db()
        second.refresh_from_db()

        self.assertEqual(
            first.career,
            self.data,
        )

        self.assertEqual(
            second.career,
            self.software,
        )

    def test_cross_profile_goal_id_is_rejected(
        self,
    ):
        other_goal = (
            CareerGoal.objects.create(
                student_profile=(
                    self.other_profile
                ),
                career=self.cloud,
                target_role=(
                    self.cloud.name
                ),
                is_primary=True,
            )
        )

        response = self.patch_profile(
            [
                {
                    "id": other_goal.id,
                    "career_id": (
                        self.software.id
                    ),
                }
            ]
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        other_goal.refresh_from_db()

        self.assertEqual(
            other_goal.career,
            self.cloud,
        )
