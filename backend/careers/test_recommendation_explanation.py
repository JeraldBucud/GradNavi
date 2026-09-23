from types import (
    SimpleNamespace,
)
from unittest.mock import (
    Mock,
    patch,
)

from django.contrib.auth import (
    get_user_model,
)
from rest_framework import (
    status,
)
from rest_framework.test import (
    APITestCase,
)
from rest_framework_simplejwt.tokens import (
    RefreshToken,
)

from ai_services.schemas.outputs import (
    CareerMatchExplanation,
)
from careers.services.recommendation_explanation import (
    EXPLANATION_VERSION,
)
from profiles.models import (
    StudentProfile,
)


class TopMatchExplanationAPITests(
    APITestCase
):
    def setUp(
        self,
    ):
        user_model = (
            get_user_model()
        )

        self.user = (
            user_model
            .objects
            .create_user(
                email=(
                    "explanation-api@"
                    "gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        self.profile = (
            StudentProfile
            .objects
            .create(
                user=(
                    self.user
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

        self.url = (
            "/api/v1/recommendations/"
            "top-explanation/"
        )


    def snapshot(
        self,
    ):
        return SimpleNamespace(
            payload={
                "recommendations": [
                    {
                        "career_id": 101,
                        "career_name": (
                            "Software Engineer"
                        ),
                        "recommendation_score": (
                            "84.80"
                        ),
                        "rank": 1,
                        "matched_competencies": [
                            "Critical Thinking",
                            "Programming",
                        ],
                        "matched_technologies": [
                            "PostgreSQL",
                        ],
                        "missing_competencies": [
                            "Active Learning",
                        ],
                    }
                ]
            },
            save=Mock(),
        )


    def request_explanation(
        self,
    ):
        return self.client.get(
            self.url,
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )


    def test_first_request_generates_and_caches(
        self,
    ):
        snapshot = (
            self.snapshot()
        )

        provider = Mock()

        provider.model = (
            "gpt-test"
        )

        provider.last_usage = {
            "input_tokens": 120,
            "output_tokens": 40,
            "total_tokens": 160,
        }

        provider.generate.return_value = (
            CareerMatchExplanation(
                explanation=(
                    "Critical Thinking and Programming provide "
                    "strong evidence for this match."
                ),
                is_ai_generated=True,
            )
        )

        with (
            patch(
                "careers.views."
                "build_recommendation_cache_key",
                return_value=(
                    object()
                ),
            ),
            patch(
                "careers.views."
                "get_valid_recommendation_snapshot",
                return_value=(
                    snapshot
                ),
            ),
            patch(
                "careers.views."
                "resolve_text_model",
                return_value=(
                    "gpt-test"
                ),
            ),
            patch(
                "careers.views."
                "OpenAITextProvider",
                return_value=(
                    provider
                ),
            ) as provider_class,
        ):
            response = (
                self.request_explanation()
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        provider_class.assert_called_once()

        provider.generate.assert_called_once()

        self.assertFalse(
            response.data[
                "data"
            ][
                "cached"
            ]
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "career_id"
            ],
            101,
        )

        self.assertEqual(
            response.data[
                "data"
            ][
                "usage"
            ][
                "total_tokens"
            ],
            160,
        )

        self.assertIn(
            "top_match_explanation",
            snapshot.payload,
        )

        snapshot.save.assert_called_once()


    def test_cached_request_skips_ai_provider(
        self,
    ):
        snapshot = (
            self.snapshot()
        )

        snapshot.payload[
            "top_match_explanation"
        ] = {
            "career_id": 101,
            "match_explanation": (
                "Cached explanation."
            ),
            "is_ai_generated": True,
            "model": "gpt-test",
            "version": (
                EXPLANATION_VERSION
            ),
            "usage": {
                "input_tokens": 120,
                "output_tokens": 40,
                "total_tokens": 160,
            },
        }

        with (
            patch(
                "careers.views."
                "build_recommendation_cache_key",
                return_value=(
                    object()
                ),
            ),
            patch(
                "careers.views."
                "get_valid_recommendation_snapshot",
                return_value=(
                    snapshot
                ),
            ),
            patch(
                "careers.views."
                "resolve_text_model",
                return_value=(
                    "gpt-test"
                ),
            ),
            patch(
                "careers.views."
                "OpenAITextProvider",
            ) as provider_class,
        ):
            response = (
                self.request_explanation()
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data[
                "data"
            ][
                "cached"
            ]
        )

        provider_class.assert_not_called()

        snapshot.save.assert_not_called()
