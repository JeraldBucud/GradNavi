from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from careers.services.readiness_scoring import (
    CareerNotAvailableError,
    CareerNotFoundError,
    CareerReadinessResult,
    GapStatus,
    ReadinessStatus,
    SkillGapResult,
)
from profiles.models import StudentProfile


class SelectedCareerReadinessAPITests(
    APITestCase
):
    def setUp(self):
        user_model = get_user_model()

        self.url = (
            "/api/v1/readiness/"
        )

        self.user = (
            user_model.objects.create_user(
                email=(
                    "readiness-api-a"
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

        self.access_token = str(
            RefreshToken
            .for_user(self.user)
            .access_token
        )


    def authenticated_get(
        self,
        path=None,
    ):
        return self.client.get(
            path or (
                f"{self.url}?career_id=10"
            ),
            HTTP_AUTHORIZATION=(
                f"Bearer {self.access_token}"
            ),
        )


    def make_gap(
        self,
        *,
        career_skill_id,
        skill_id,
        skill_name,
        gap_status,
        current_proficiency,
        current_score,
        required_level,
        gap_amount,
        attainment_percentage,
        importance,
    ):
        return SkillGapResult(
            career_skill_id=(
                career_skill_id
            ),
            skill_id=skill_id,
            skill_name=skill_name,
            concept_type="skill",
            source_domain=(
                "onet_essential_skills"
            ),
            student_proficiency_level=(
                current_proficiency
            ),
            student_proficiency_score=(
                current_score
            ),
            required_level=(
                required_level
            ),
            importance=importance,
            gap_amount=gap_amount,
            attainment_ratio=(
                attainment_percentage
                / Decimal("100")
            ),
            attainment_percentage=(
                attainment_percentage
            ),
            weighted_contribution=(
                Decimal("0")
            ),
            gap_status=gap_status,
        )


    def make_result(self):
        missing = self.make_gap(
            career_skill_id=101,
            skill_id=201,
            skill_name=(
                "Computers and Electronics"
            ),
            gap_status=GapStatus.MISSING,
            current_proficiency=None,
            current_score=Decimal("0"),
            required_level=Decimal("89"),
            gap_amount=Decimal("89"),
            attainment_percentage=(
                Decimal("0")
            ),
            importance=Decimal("93.75"),
        )

        below = self.make_gap(
            career_skill_id=102,
            skill_id=202,
            skill_name="Critical Thinking",
            gap_status=(
                GapStatus.BELOW_REQUIREMENT
            ),
            current_proficiency=(
                "developing"
            ),
            current_score=Decimal("50"),
            required_level=Decimal("58.86"),
            gap_amount=Decimal("8.86"),
            attainment_percentage=(
                Decimal("84.95")
            ),
            importance=Decimal("72"),
        )

        meets = self.make_gap(
            career_skill_id=103,
            skill_id=203,
            skill_name="Programming",
            gap_status=(
                GapStatus.MEETS_REQUIREMENT
            ),
            current_proficiency=(
                "advanced"
            ),
            current_score=Decimal("100"),
            required_level=Decimal("70"),
            gap_amount=Decimal("0"),
            attainment_percentage=(
                Decimal("100")
            ),
            importance=Decimal("80"),
        )

        return CareerReadinessResult(
            career_id=10,
            career_name="Software Engineer",
            score_status=(
                ReadinessStatus.SCORED
            ),
            readiness_score=(
                Decimal("68.00")
            ),
            matched_requirement_count=2,
            missing_requirement_count=1,
            below_requirement_count=1,
            meets_requirement_count=1,
            skill_gaps=(
                missing,
                below,
                meets,
            ),
        )


    def test_authentication_required(self):
        response = self.client.get(
            f"{self.url}?career_id=10"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_request_user_profile_is_used(
        self,
    ):
        result = self.make_result()

        path = (
            f"{self.url}"
            "?career_id=10"
            "&student_profile_id=9999"
            "&user_id=9999"
        )

        with patch(
            (
                "careers.views."
                "calculate_selected_career_readiness"
            ),
            return_value=result,
        ) as calculate_mock:
            response = (
                self.authenticated_get(
                    path
                )
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        calculate_mock.assert_called_once_with(
            student_profile_id=(
                self.profile.id
            ),
            career_id=10,
        )


    def test_complete_readiness_contract(
        self,
    ):
        result = self.make_result()

        with patch(
            (
                "careers.views."
                "calculate_selected_career_readiness"
            ),
            return_value=result,
        ):
            response = (
                self.authenticated_get()
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data["data"]

        self.assertEqual(
            set(data),
            {
                "career_id",
                "career_name",
                "score_status",
                "readiness_score",
                "meets_requirement_count",
                "below_requirement_count",
                "missing_requirement_count",
                "total_requirement_count",
                "requirements",
            },
        )

        self.assertEqual(
            data["career_id"],
            10,
        )

        self.assertEqual(
            data["career_name"],
            "Software Engineer",
        )

        self.assertEqual(
            data["score_status"],
            "scored",
        )

        self.assertEqual(
            data["readiness_score"],
            "68.00",
        )

        self.assertEqual(
            data["meets_requirement_count"],
            1,
        )

        self.assertEqual(
            data["below_requirement_count"],
            1,
        )

        self.assertEqual(
            data["missing_requirement_count"],
            1,
        )

        self.assertEqual(
            data["total_requirement_count"],
            3,
        )


    def test_all_requirement_statuses_are_exposed(
        self,
    ):
        result = self.make_result()

        with patch(
            (
                "careers.views."
                "calculate_selected_career_readiness"
            ),
            return_value=result,
        ):
            response = (
                self.authenticated_get()
            )

        requirements = (
            response
            .data["data"]
            ["requirements"]
        )

        self.assertEqual(
            [
                item["status"]
                for item in requirements
            ],
            [
                "missing",
                "below_requirement",
                "meets_requirement",
            ],
        )

        self.assertEqual(
            requirements[1][
                "current_proficiency"
            ],
            "developing",
        )

        self.assertEqual(
            requirements[1][
                "current_score"
            ],
            "50.00",
        )

        self.assertEqual(
            requirements[1][
                "required_level"
            ],
            "58.86",
        )

        self.assertEqual(
            requirements[1][
                "gap_amount"
            ],
            "8.86",
        )

        self.assertEqual(
            requirements[1][
                "attainment_percentage"
            ],
            "84.95",
        )


    def test_invalid_career_id_is_rejected(
        self,
    ):
        response = self.authenticated_get(
            f"{self.url}?career_id=abc"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_missing_career_returns_not_found(
        self,
    ):
        with patch(
            (
                "careers.views."
                "calculate_selected_career_readiness"
            ),
            side_effect=(
                CareerNotFoundError()
            ),
        ):
            response = (
                self.authenticated_get(
                    (
                        f"{self.url}"
                        "?career_id=999"
                    )
                )
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


    def test_inactive_career_is_rejected(
        self,
    ):
        with patch(
            (
                "careers.views."
                "calculate_selected_career_readiness"
            ),
            side_effect=(
                CareerNotAvailableError()
            ),
        ):
            response = (
                self.authenticated_get(
                    (
                        f"{self.url}"
                        "?career_id=12"
                    )
                )
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_missing_profile_returns_not_found(
        self,
    ):
        self.profile.delete()

        response = (
            self.authenticated_get()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
    def test_readiness_output_is_independent_of_text_ai_provider(
        self,
    ):
        deterministic_result = (
            self.make_result()
        )

        with patch(
            (
                "careers.views."
                "calculate_selected_career_readiness"
            ),
            return_value=(
                deterministic_result
            ),
        ):
            baseline_response = (
                self.authenticated_get()
            )

        self.assertEqual(
            baseline_response.status_code,
            status.HTTP_200_OK,
        )

        baseline_data = (
            baseline_response.data[
                "data"
            ]
        )

        with (
            patch(
                (
                    "careers.views."
                    "calculate_selected_career_readiness"
                ),
                return_value=(
                    deterministic_result
                ),
            ),
            patch(
                (
                    "careers.views."
                    "OpenAITextProvider"
                )
            ) as ai_provider,
        ):
            ai_provider.side_effect = (
                RuntimeError(
                    "Text AI provider must not be used."
                )
            )

            protected_response = (
                self.authenticated_get()
            )

        self.assertEqual(
            protected_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            protected_response.data[
                "data"
            ],
            baseline_data,
        )

        self.assertEqual(
            protected_response.data[
                "data"
            ][
                "readiness_score"
            ],
            "68.00",
        )

        ai_provider.assert_not_called()
