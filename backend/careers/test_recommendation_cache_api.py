from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from careers.models import (
    Career,
    RecommendationSnapshot,
)

from careers.services.recommendation_scoring import (
    ScoreStatus,
)

from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


class RecommendationCacheAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            email="cache-api@gradnavi.test",
            password="StrongPassword123!",
        )

        self.profile = (
            StudentProfile.objects.create(
                user=self.user,
            )
        )

        access_token = str(
            RefreshToken
            .for_user(self.user)
            .access_token
        )

        self.authorization = (
            f"Bearer {access_token}"
        )

        self.url = (
            "/api/v1/recommendations/"
        )


    def get_recommendations(self):
        return self.client.get(
            self.url,
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )


    def composite_result(
        self,
        *,
        career_id=101,
        career_name="Software Engineer",
        recommendation_score=(
            Decimal("82.50")
        ),
    ):
        competency_result = (
            SimpleNamespace(
                matched_competencies=(
                    "Critical Thinking",
                ),
                missing_competencies=(
                    "Systems Analysis",
                ),
                esco_essential_skills=(
                    "Communication",
                ),
                esco_optional_skills=(),
            )
        )

        technology_result = (
            SimpleNamespace(
                matched_technologies=(
                    "Python",
                ),
                missing_technologies=(
                    "Docker",
                ),
            )
        )

        semantic_result = (
            SimpleNamespace(
                essential_esco_count=1,
            )
        )

        return SimpleNamespace(
            career_id=career_id,
            career_name=career_name,
            recommendation_score=(
                recommendation_score
            ),
            rank=1,

            competency_score=(
                Decimal("60.00")
            ),
            competency_normalized_score=(
                Decimal("70.000000")
            ),
            competency_status=(
                ScoreStatus.SCORED
            ),

            technology_score=(
                Decimal("80.00")
            ),
            technology_normalized_score=(
                Decimal("90.000000")
            ),
            technology_status=(
                ScoreStatus.SCORED
            ),
            technology_student_alignment_ratio=(
                Decimal("0.500000")
            ),
            technology_active=True,

            semantic_alignment_score=(
                Decimal("85.00")
            ),
            semantic_normalized_score=(
                Decimal("95.000000")
            ),
            semantic_context_mode=(
                "identity_esco"
            ),

            effective_competency_weight=(
                Decimal("0.200000")
            ),
            effective_technology_weight=(
                Decimal("0.200000")
            ),
            effective_semantic_weight=(
                Decimal("0.600000")
            ),

            competency_result=(
                competency_result
            ),
            technology_result=(
                technology_result
            ),
            semantic_result=(
                semantic_result
            ),
        )


    def composite_report(
        self,
        *,
        career_name="Software Engineer",
    ):
        result = self.composite_result(
            career_name=career_name,
        )

        return SimpleNamespace(
            model="text-embedding-3-small",
            prompt_tokens=120,
            total_tokens=120,
            career_count=1,
            results=(
                result,
            ),
        )


    def run_cache_miss(
        self,
        *,
        report=None,
    ):
        if report is None:
            report = (
                self.composite_report()
            )

        provider = object()

        with (
            patch(
                "careers.views."
                "OpenAIEmbeddingProvider",
                return_value=provider,
            ) as provider_mock,
            patch(
                "careers.views."
                "generate_composite_recommendations",
                return_value=report,
            ) as generate_mock,
        ):
            response = (
                self.get_recommendations()
            )

        return (
            response,
            provider_mock,
            generate_mock,
        )


    def test_first_request_generates_and_stores_snapshot(
        self,
    ):
        (
            response,
            provider_mock,
            generate_mock,
        ) = self.run_cache_miss()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        provider_mock.assert_called_once()

        generate_mock.assert_called_once()

        snapshot = (
            RecommendationSnapshot.objects.get(
                student_profile=self.profile,
            )
        )

        self.assertEqual(
            snapshot.payload,
            response.data["data"],
        )

        self.assertEqual(
            snapshot.embedding_model,
            "text-embedding-3-small",
        )

        self.assertEqual(
            snapshot.prompt_tokens,
            120,
        )

        self.assertEqual(
            snapshot.total_tokens,
            120,
        )

        self.assertEqual(
            snapshot.career_count,
            1,
        )


    def test_second_identical_request_uses_snapshot_without_ai(
        self,
    ):
        first_response, _, _ = (
            self.run_cache_miss()
        )

        with (
            patch(
                "careers.views."
                "OpenAIEmbeddingProvider"
            ) as provider_mock,
            patch(
                "careers.views."
                "generate_composite_recommendations"
            ) as generate_mock,
        ):
            second_response = (
                self.get_recommendations()
            )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        provider_mock.assert_not_called()

        generate_mock.assert_not_called()

        self.assertEqual(
            second_response.data,
            first_response.data,
        )

        self.assertEqual(
            RecommendationSnapshot.objects.filter(
                student_profile=self.profile,
            ).count(),
            1,
        )


    def test_profile_change_forces_new_recommendation_run(
        self,
    ):
        self.run_cache_miss()

        skill = Skill.objects.create(
            name="Cache API Critical Thinking",
            concept_type=(
                Skill.ConceptType.SKILL
            ),
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .DEVELOPING
            ),
        )

        updated_report = (
            self.composite_report(
                career_name="Updated Career",
            )
        )

        (
            response,
            provider_mock,
            generate_mock,
        ) = self.run_cache_miss(
            report=updated_report,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        provider_mock.assert_called_once()

        generate_mock.assert_called_once()

        self.assertEqual(
            response.data["data"]
            ["recommendations"][0]
            ["career_name"],
            "Updated Career",
        )

        self.assertEqual(
            RecommendationSnapshot.objects.filter(
                student_profile=self.profile,
            ).count(),
            1,
        )


    def test_reference_change_forces_new_recommendation_run(
        self,
    ):
        self.run_cache_miss()

        Career.objects.create(
            name="Cache API New Career",
            description="New reference data.",
            category="Technology",
            active=True,
        )

        updated_report = (
            self.composite_report(
                career_name="Reference Updated Career",
            )
        )

        (
            response,
            provider_mock,
            generate_mock,
        ) = self.run_cache_miss(
            report=updated_report,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        provider_mock.assert_called_once()

        generate_mock.assert_called_once()

        self.assertEqual(
            response.data["data"]
            ["recommendations"][0]
            ["career_name"],
            "Reference Updated Career",
        )


    def test_cache_hit_keeps_public_response_contract_unchanged(
        self,
    ):
        first_response, _, _ = (
            self.run_cache_miss()
        )

        second_response = (
            self.get_recommendations()
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            set(
                second_response.data
                ["data"]
            ),
            {
                "scoring_model",
                "embedding_model",
                "career_count",
                "base_weights",
                "recommendations",
            },
        )

        self.assertEqual(
            second_response.data,
            first_response.data,
        )


    def test_snapshot_is_private_to_authenticated_profile(
        self,
    ):
        first_response, _, _ = (
            self.run_cache_miss()
        )

        user_model = get_user_model()

        other_user = (
            user_model.objects.create_user(
                email=(
                    "cache-api-other"
                    "@gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        other_profile = (
            StudentProfile.objects.create(
                user=other_user,
            )
        )

        other_token = str(
            RefreshToken
            .for_user(other_user)
            .access_token
        )

        other_report = (
            self.composite_report(
                career_name="Other Student Career",
            )
        )

        provider = object()

        with (
            patch(
                "careers.views."
                "OpenAIEmbeddingProvider",
                return_value=provider,
            ),
            patch(
                "careers.views."
                "generate_composite_recommendations",
                return_value=other_report,
            ),
        ):
            other_response = (
                self.client.get(
                    self.url,
                    HTTP_AUTHORIZATION=(
                        f"Bearer {other_token}"
                    ),
                )
            )

        self.assertEqual(
            other_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            first_response.data
            ["data"]
            ["recommendations"][0]
            ["career_name"],
            "Software Engineer",
        )

        self.assertEqual(
            other_response.data
            ["data"]
            ["recommendations"][0]
            ["career_name"],
            "Other Student Career",
        )

        self.assertTrue(
            RecommendationSnapshot.objects.filter(
                student_profile=self.profile,
            ).exists()
        )

        self.assertTrue(
            RecommendationSnapshot.objects.filter(
                student_profile=other_profile,
            ).exists()
        )
