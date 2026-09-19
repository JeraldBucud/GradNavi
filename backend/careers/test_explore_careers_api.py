from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from ai_services.exceptions import (
    AIProviderError,
)
from careers.models import (
    Career,
    RecommendationSnapshot,
    StudentCareerEvaluation,
)
from careers.services.recommendation_cache import (
    build_recommendation_cache_key,
    store_recommendation_snapshot,
)
from careers.services.recommendation_scoring import (
    ScoreStatus,
)
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


class ExploreCareersAPITests(
    APITestCase
):

    def setUp(
        self,
    ):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "explore-api@"
                    "gradnavi.test"
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

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                self.authorization
            )
        )

        self.careers = []

        for index in range(
            1,
            16,
        ):
            category = (
                "Technology"
                if index <= 10
                else "Business"
            )

            career = (
                Career.objects.create(
                    name=(
                        "Explore API Career "
                        f"{index:02d}"
                    ),
                    description=(
                        "Explore API catalogue "
                        f"description {index}."
                    ),
                    category=category,
                    active=True,
                )
            )

            self.careers.append(
                career
            )

        self.inactive_career = (
            Career.objects.create(
                name=(
                    "Explore API "
                    "Inactive Career"
                ),
                description=(
                    "Inactive API record."
                ),
                category="Technology",
                active=False,
            )
        )

        self.list_url = (
            "/api/v1/explore-careers/"
        )

        self.guidance_url = (
            "/api/v1/guidance-careers/"
        )

        self.store_current_snapshot()


    def store_current_snapshot(
        self,
    ):
        cache_key = (
            build_recommendation_cache_key(
                student_profile=self.profile,
            )
        )

        recommendations = []

        for rank, career in enumerate(
            self.careers,
            start=1,
        ):
            score = (
                Decimal("100.00")
                - Decimal(rank)
            )

            recommendations.append(
                {
                    "career_id": career.id,
                    "career_name": career.name,
                    "recommendation_score": (
                        f"{score:.2f}"
                    ),
                    "rank": rank,
                }
            )

        self.snapshot = (
            store_recommendation_snapshot(
                student_profile=self.profile,
                payload={
                    "scoring_model": (
                        cache_key
                        .scoring_version
                    ),
                    "career_count": (
                        len(
                            recommendations
                        )
                    ),
                    "recommendations": (
                        recommendations
                    ),
                },
                embedding_model=(
                    "test-embedding-model"
                ),
                prompt_tokens=0,
                total_tokens=0,
                career_count=(
                    len(
                        recommendations
                    )
                ),
                cache_key=cache_key,
            )
        )

        return self.snapshot


    def refresh_result(
        self,
        *,
        career,
        rank=1,
        score=Decimal("90.00"),
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
            career_id=career.id,
            career_name=career.name,
            recommendation_score=score,
            rank=rank,

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


    def refresh_report(
        self,
        *,
        career,
    ):
        result = (
            self.refresh_result(
                career=career,
            )
        )

        return SimpleNamespace(
            model=(
                "text-embedding-3-small"
            ),
            prompt_tokens=120,
            total_tokens=120,
            career_count=1,
            results=(
                result,
            ),
        )


    def test_list_requires_authentication(
        self,
    ):
        self.client.credentials()

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_list_uses_default_twelve_item_page(
        self,
    ):
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
            response = self.client.get(
                self.list_url
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        provider_mock.assert_not_called()
        generate_mock.assert_not_called()

        data = response.data[
            "data"
        ]

        self.assertEqual(
            len(
                data[
                    "results"
                ]
            ),
            12,
        )

        pagination = data[
            "pagination"
        ]

        self.assertEqual(
            pagination[
                "page"
            ],
            1,
        )

        self.assertEqual(
            pagination[
                "page_size"
            ],
            12,
        )

        self.assertEqual(
            pagination[
                "total_count"
            ],
            15,
        )

        self.assertEqual(
            pagination[
                "total_pages"
            ],
            2,
        )

        self.assertFalse(
            pagination[
                "has_previous"
            ]
        )

        self.assertTrue(
            pagination[
                "has_next"
            ]
        )

        self.assertEqual(
            data[
                "recommended_limit"
            ],
            7,
        )


    def test_second_page_returns_remaining_careers(
        self,
    ):
        response = self.client.get(
            self.list_url,
            {
                "page": 2,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data[
            "data"
        ]

        self.assertEqual(
            len(
                data[
                    "results"
                ]
            ),
            3,
        )

        self.assertTrue(
            data[
                "pagination"
            ][
                "has_previous"
            ]
        )

        self.assertFalse(
            data[
                "pagination"
            ][
                "has_next"
            ]
        )


    def test_search_filters_server_side(
        self,
    ):
        response = self.client.get(
            self.list_url,
            {
                "search": (
                    "Career 15"
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data[
            "data"
        ][
            "results"
        ]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0][
                "career_id"
            ],
            self.careers[14].id,
        )


    def test_category_filter_is_server_side(
        self,
    ):
        response = self.client.get(
            self.list_url,
            {
                "category": (
                    "Business"
                ),
                "page_size": 50,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data[
            "data"
        ]

        self.assertEqual(
            len(
                data[
                    "results"
                ]
            ),
            5,
        )

        self.assertTrue(
            all(
                item[
                    "category"
                ]
                == "Business"
                for item in data[
                    "results"
                ]
            )
        )

        self.assertEqual(
            data[
                "filters"
            ][
                "categories"
            ],
            [
                "Business",
                "Technology",
            ],
        )


    def test_recommended_status_returns_top_seven(
        self,
    ):
        response = self.client.get(
            self.list_url,
            {
                "status": (
                    "recommended"
                ),
                "page_size": 50,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data[
            "data"
        ][
            "results"
        ]

        self.assertEqual(
            len(results),
            7,
        )

        self.assertTrue(
            all(
                item[
                    "recommended"
                ]
                for item in results
            )
        )


    def test_not_evaluated_status_excludes_top_seven(
        self,
    ):
        response = self.client.get(
            self.list_url,
            {
                "status": (
                    "not_evaluated"
                ),
                "page_size": 50,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data[
            "data"
        ][
            "results"
        ]

        self.assertEqual(
            len(results),
            8,
        )

        self.assertTrue(
            all(
                not item[
                    "recommended"
                ]
                for item in results
            )
        )


    def test_detail_returns_student_specific_state(
        self,
    ):
        career = self.careers[0]

        response = self.client.get(
            (
                "/api/v1/"
                "explore-careers/"
                f"{career.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data[
            "data"
        ]

        self.assertEqual(
            data[
                "career_id"
            ],
            career.id,
        )

        self.assertTrue(
            data[
                "recommended"
            ]
        )

        self.assertEqual(
            data[
                "recommendation_rank"
            ],
            1,
        )

        self.assertEqual(
            data[
                "match_score"
            ],
            "99.00",
        )


    def test_inactive_detail_returns_not_found(
        self,
    ):
        response = self.client.get(
            (
                "/api/v1/"
                "explore-careers/"
                f"{self.inactive_career.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


    def test_evaluate_non_recommended_career(
        self,
    ):
        career = self.careers[7]

        response = self.client.post(
            (
                "/api/v1/"
                "explore-careers/"
                f"{career.id}/"
                "evaluate/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.data[
            "data"
        ]

        self.assertFalse(
            data[
                "recommendation_refreshed"
            ]
        )

        self.assertEqual(
            data[
                "career"
            ][
                "status"
            ],
            "evaluated",
        )

        self.assertTrue(
            data[
                "career"
            ][
                "evaluated"
            ]
        )

        self.assertEqual(
            data[
                "evaluation"
            ][
                "career_id"
            ],
            career.id,
        )

        self.assertTrue(
            StudentCareerEvaluation.objects.filter(
                student_profile=(
                    self.profile
                ),
                career=career,
            ).exists()
        )


    def test_guidance_list_adds_explicit_evaluation(
        self,
    ):
        career = self.careers[7]

        self.client.post(
            (
                "/api/v1/"
                "explore-careers/"
                f"{career.id}/"
                "evaluate/"
            ),
            {},
            format="json",
        )

        response = self.client.get(
            self.guidance_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        careers = response.data[
            "data"
        ][
            "careers"
        ]

        self.assertEqual(
            len(careers),
            8,
        )

        self.assertEqual(
            [
                item[
                    "career_id"
                ]
                for item in careers[
                    :7
                ]
            ],
            [
                item.id
                for item in self.careers[
                    :7
                ]
            ],
        )

        self.assertEqual(
            careers[7][
                "career_id"
            ],
            career.id,
        )


    def test_page_size_above_fifty_is_rejected(
        self,
    ):
        response = self.client.get(
            self.list_url,
            {
                "page_size": 51,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_missing_snapshot_is_refreshed(
        self,
    ):
        self.snapshot.delete()

        report = (
            self.refresh_report(
                career=self.careers[0],
            )
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
            response = self.client.get(
                self.list_url
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        provider_mock.assert_called_once()

        generate_mock.assert_called_once()

        self.assertEqual(
            RecommendationSnapshot.objects.filter(
                student_profile=(
                    self.profile
                ),
            ).count(),
            1,
        )


    def test_stale_snapshot_is_refreshed_before_evaluation(
        self,
    ):
        target = self.careers[7]

        skill = Skill.objects.create(
            name=(
                "Explore API "
                "Refresh Skill"
            ),
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

        report = (
            self.refresh_report(
                career=target,
            )
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
            response = self.client.post(
                (
                    "/api/v1/"
                    "explore-careers/"
                    f"{target.id}/"
                    "evaluate/"
                ),
                {},
                format="json",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        provider_mock.assert_called_once()

        generate_mock.assert_called_once()

        self.assertTrue(
            response.data[
                "data"
            ][
                "recommendation_refreshed"
            ]
        )

        self.assertTrue(
            StudentCareerEvaluation.objects.filter(
                student_profile=(
                    self.profile
                ),
                career=target,
            ).exists()
        )


    def test_refresh_provider_failure_returns_503(
        self,
    ):
        self.snapshot.delete()

        with patch(
            "careers.views."
            "OpenAIEmbeddingProvider",
            side_effect=(
                AIProviderError(
                    "Provider unavailable."
                )
            ),
        ):
            response = self.client.get(
                self.list_url
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
