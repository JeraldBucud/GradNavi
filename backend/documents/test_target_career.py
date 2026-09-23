from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from careers.models import Career
from documents.services.target_career import (
    TargetCareerNotAvailableError,
    resolve_document_target_career,
)
from profiles.models import (
    CareerGoal,
    StudentProfile,
)


class DocumentTargetCareerTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "document-target-a@gradnavi.test"
                ),
                password="StrongPassword123!",
            )
        )

        self.profile = (
            StudentProfile.objects.create(
                user=self.user,
            )
        )

        self.other_user = (
            user_model.objects.create_user(
                email=(
                    "document-target-b@gradnavi.test"
                ),
                password="StrongPassword123!",
            )
        )

        self.other_profile = (
            StudentProfile.objects.create(
                user=self.other_user,
            )
        )

        self.saved_career = (
            Career.objects.create(
                name="Software Engineer",
                active=True,
            )
        )

        self.recommended_career = (
            Career.objects.create(
                name="Cloud Engineer",
                active=True,
            )
        )

        self.unavailable_career = (
            Career.objects.create(
                name="AI Engineer",
                active=True,
            )
        )

        self.inactive_career = (
            Career.objects.create(
                name="Inactive Career",
                active=False,
            )
        )

        CareerGoal.objects.create(
            student_profile=self.profile,
            career=self.saved_career,
            target_role=(
                self.saved_career.name
            ),
            is_primary=True,
        )


    def test_saved_career_goal_is_available(
        self,
    ):
        with patch(
            "documents.services.target_career."
            "build_recommendation_cache_key"
        ) as cache_key_mock:
            result = (
                resolve_document_target_career(
                    student_profile=(
                        self.profile
                    ),
                    career_id=(
                        self.saved_career.id
                    ),
                )
            )

        self.assertEqual(
            result,
            self.saved_career,
        )

        cache_key_mock.assert_not_called()


    def test_valid_recommendation_is_available(
        self,
    ):
        snapshot = SimpleNamespace(
            payload={
                "recommendations": [
                    {
                        "career_id": (
                            self.recommended_career.id
                        ),
                        "career_name": (
                            self.recommended_career.name
                        ),
                    }
                ]
            }
        )

        with (
            patch(
                "documents.services.target_career."
                "build_recommendation_cache_key",
                return_value="cache-key",
            ),
            patch(
                "documents.services.target_career."
                "get_valid_recommendation_snapshot",
                return_value=snapshot,
            ) as snapshot_mock,
        ):
            result = (
                resolve_document_target_career(
                    student_profile=(
                        self.profile
                    ),
                    career_id=(
                        self.recommended_career.id
                    ),
                )
            )

        self.assertEqual(
            result,
            self.recommended_career,
        )

        snapshot_mock.assert_called_once_with(
            student_profile=self.profile,
            cache_key="cache-key",
        )


    def test_active_arbitrary_career_is_rejected(
        self,
    ):
        with (
            patch(
                "documents.services.target_career."
                "build_recommendation_cache_key",
                return_value="cache-key",
            ),
            patch(
                "documents.services.target_career."
                "get_valid_recommendation_snapshot",
                return_value=None,
            ),
        ):
            with self.assertRaises(
                TargetCareerNotAvailableError
            ):
                resolve_document_target_career(
                    student_profile=(
                        self.profile
                    ),
                    career_id=(
                        self.unavailable_career.id
                    ),
                )


    def test_stale_recommendation_is_rejected(
        self,
    ):
        with (
            patch(
                "documents.services.target_career."
                "build_recommendation_cache_key",
                return_value="cache-key",
            ),
            patch(
                "documents.services.target_career."
                "get_valid_recommendation_snapshot",
                return_value=None,
            ),
        ):
            with self.assertRaises(
                TargetCareerNotAvailableError
            ):
                resolve_document_target_career(
                    student_profile=(
                        self.profile
                    ),
                    career_id=(
                        self.recommended_career.id
                    ),
                )


    def test_other_student_goal_does_not_grant_access(
        self,
    ):
        CareerGoal.objects.create(
            student_profile=self.other_profile,
            career=self.unavailable_career,
            target_role=(
                self.unavailable_career.name
            ),
            is_primary=True,
        )

        with (
            patch(
                "documents.services.target_career."
                "build_recommendation_cache_key",
                return_value="cache-key",
            ),
            patch(
                "documents.services.target_career."
                "get_valid_recommendation_snapshot",
                return_value=None,
            ),
        ):
            with self.assertRaises(
                TargetCareerNotAvailableError
            ):
                resolve_document_target_career(
                    student_profile=(
                        self.profile
                    ),
                    career_id=(
                        self.unavailable_career.id
                    ),
                )


    def test_inactive_career_is_rejected(
        self,
    ):
        with patch(
            "documents.services.target_career."
            "build_recommendation_cache_key"
        ) as cache_key_mock:
            with self.assertRaises(
                TargetCareerNotAvailableError
            ):
                resolve_document_target_career(
                    student_profile=(
                        self.profile
                    ),
                    career_id=(
                        self.inactive_career.id
                    ),
                )

        cache_key_mock.assert_not_called()


    def test_malformed_recommendation_payload_is_rejected(
        self,
    ):
        snapshot = SimpleNamespace(
            payload={
                "recommendations": [
                    None,
                    "invalid",
                    {
                        "career_id": "invalid",
                    },
                ]
            }
        )

        with (
            patch(
                "documents.services.target_career."
                "build_recommendation_cache_key",
                return_value="cache-key",
            ),
            patch(
                "documents.services.target_career."
                "get_valid_recommendation_snapshot",
                return_value=snapshot,
            ),
        ):
            with self.assertRaises(
                TargetCareerNotAvailableError
            ):
                resolve_document_target_career(
                    student_profile=(
                        self.profile
                    ),
                    career_id=(
                        self.unavailable_career.id
                    ),
                )


    def test_invalid_career_identifier_is_rejected(
        self,
    ):
        invalid_values = (
            None,
            "",
            0,
            -1,
            True,
            "not-a-career",
        )

        for value in invalid_values:
            with self.subTest(
                career_id=value,
            ):
                with self.assertRaises(
                    TargetCareerNotAvailableError
                ):
                    resolve_document_target_career(
                        student_profile=(
                            self.profile
                        ),
                        career_id=value,
                    )
