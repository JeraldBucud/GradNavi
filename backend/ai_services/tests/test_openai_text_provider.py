import json
from types import (
    SimpleNamespace,
)
from unittest import (
    TestCase,
)
from unittest.mock import (
    Mock,
    patch,
)

from ai_services.exceptions import (
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIResponseValidationError,
)
from ai_services.prompts.career_match_explanation import (
    build_career_match_explanation_prompt,
)
from ai_services.providers.openai_text import (
    OpenAITextProvider,
)
from ai_services.schemas.outputs import (
    CareerMatchExplanation,
)


class OpenAITextProviderTests(
    TestCase
):
    def recommendation(
        self,
    ):
        return {
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


    def test_generate_returns_validated_output(
        self,
    ):
        response = SimpleNamespace(
            status="completed",
            output_text=(
                json.dumps(
                    {
                        "explanation": (
                            "Critical Thinking, Programming, and PostgreSQL "
                            "provide strong evidence for this match. "
                            "Active Learning is one area to continue developing."
                        ),
                        "is_ai_generated": True,
                    }
                )
            ),
            usage=SimpleNamespace(
                input_tokens=120,
                output_tokens=40,
                total_tokens=160,
            ),
        )

        create_mock = Mock(
            return_value=(
                response
            )
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=(
                    create_mock
                )
            )
        )

        provider = (
            OpenAITextProvider(
                model=(
                    "gpt-test"
                ),
                client=(
                    client
                ),
            )
        )

        result = (
            provider.generate(
                prompt_package=(
                    build_career_match_explanation_prompt(
                        self.recommendation()
                    )
                ),
                output_model=(
                    CareerMatchExplanation
                ),
            )
        )

        self.assertIsInstance(
            result,
            CareerMatchExplanation,
        )

        self.assertTrue(
            result.is_ai_generated
        )

        self.assertEqual(
            provider.last_usage[
                "total_tokens"
            ],
            160,
        )

        kwargs = (
            create_mock
            .call_args
            .kwargs
        )

        self.assertFalse(
            kwargs[
                "store"
            ]
        )

        self.assertEqual(
            kwargs[
                "reasoning"
            ][
                "effort"
            ],
            "minimal",
        )

        self.assertEqual(
            kwargs[
                "text"
            ][
                "format"
            ][
                "type"
            ],
            "json_schema",
        )

        self.assertTrue(
            kwargs[
                "text"
            ][
                "format"
            ][
                "strict"
            ]
        )


    def test_invalid_output_is_rejected(
        self,
    ):
        response = SimpleNamespace(
            status="completed",
            output_text=(
                '{"explanation": "", '
                '"is_ai_generated": true}'
            ),
            usage=None,
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=(
                        response
                    )
                )
            )
        )

        provider = (
            OpenAITextProvider(
                model=(
                    "gpt-test"
                ),
                client=(
                    client
                ),
            )
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            provider.generate(
                prompt_package=(
                    build_career_match_explanation_prompt(
                        self.recommendation()
                    )
                ),
                output_model=(
                    CareerMatchExplanation
                ),
            )
    def test_incomplete_response_is_rejected(
        self,
    ):
        response = SimpleNamespace(
            status="incomplete",
            output_text=(
                json.dumps(
                    {
                        "explanation": (
                            "This output must not be accepted."
                        ),
                        "is_ai_generated": True,
                    }
                )
            ),
            usage=None,
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=response
                )
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with self.assertRaises(
            AIResponseValidationError
        ) as error:
            provider.generate(
                prompt_package=(
                    build_career_match_explanation_prompt(
                        self.recommendation()
                    )
                ),
                output_model=(
                    CareerMatchExplanation
                ),
            )

        self.assertEqual(
            str(error.exception),
            "OpenAI response was incomplete.",
        )


    def test_non_completed_response_states_are_rejected(
        self,
    ):
        for response_status in (
            "failed",
            "cancelled",
            "queued",
            "in_progress",
        ):
            with self.subTest(
                response_status=response_status
            ):
                response = SimpleNamespace(
                    status=response_status,
                    output_text=(
                        json.dumps(
                            {
                                "explanation": (
                                    "This output must not be accepted."
                                ),
                                "is_ai_generated": True,
                            }
                        )
                    ),
                    usage=None,
                )

                client = SimpleNamespace(
                    responses=SimpleNamespace(
                        create=Mock(
                            return_value=response
                        )
                    )
                )

                provider = OpenAITextProvider(
                    model="gpt-test",
                    client=client,
                )

                with self.assertRaises(
                    AIResponseValidationError
                ) as error:
                    provider.generate(
                        prompt_package=(
                            build_career_match_explanation_prompt(
                                self.recommendation()
                            )
                        ),
                        output_model=(
                            CareerMatchExplanation
                        ),
                    )

                self.assertEqual(
                    str(error.exception),
                    (
                        "OpenAI response did not "
                        "complete successfully."
                    ),
                )


    def test_missing_response_status_is_rejected(
        self,
    ):
        response = SimpleNamespace(
            output_text=(
                json.dumps(
                    {
                        "explanation": (
                            "This output must not be accepted."
                        ),
                        "is_ai_generated": True,
                    }
                )
            ),
            usage=None,
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=response
                )
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            provider.generate(
                prompt_package=(
                    build_career_match_explanation_prompt(
                        self.recommendation()
                    )
                ),
                output_model=(
                    CareerMatchExplanation
                ),
            )


    def test_completed_response_with_empty_output_is_rejected(
        self,
    ):
        response = SimpleNamespace(
            status="completed",
            output_text="   ",
            usage=None,
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=response
                )
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with self.assertRaises(
            AIResponseValidationError
        ) as error:
            provider.generate(
                prompt_package=(
                    build_career_match_explanation_prompt(
                        self.recommendation()
                    )
                ),
                output_model=(
                    CareerMatchExplanation
                ),
            )

        self.assertEqual(
            str(error.exception),
            (
                "OpenAI response did not contain "
                "structured output text."
            ),
        )


    def test_completed_response_with_malformed_json_is_rejected(
        self,
    ):
        response = SimpleNamespace(
            status="completed",
            output_text="{not-valid-json",
            usage=None,
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=response
                )
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with self.assertRaises(
            AIResponseValidationError
        ) as error:
            provider.generate(
                prompt_package=(
                    build_career_match_explanation_prompt(
                        self.recommendation()
                    )
                ),
                output_model=(
                    CareerMatchExplanation
                ),
            )

        self.assertEqual(
            str(error.exception),
            (
                "OpenAI structured output failed "
                "GradNavi validation."
            ),
        )


    def test_timeout_is_translated_without_provider_detail(
        self,
    ):
        class FakeTimeoutError(Exception):
            pass

        create_mock = Mock(
            side_effect=FakeTimeoutError(
                "provider timeout detail secret"
            )
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=create_mock
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with patch(
            (
                "ai_services.providers.openai_text."
                "APITimeoutError"
            ),
            FakeTimeoutError,
        ):
            with self.assertRaises(
                AIProviderTimeoutError
            ) as error:
                provider.generate(
                    prompt_package=(
                        build_career_match_explanation_prompt(
                            self.recommendation()
                        )
                    ),
                    output_model=(
                        CareerMatchExplanation
                    ),
                )

        self.assertEqual(
            str(error.exception),
            (
                "OpenAI text-generation request "
                "timed out."
            ),
        )

        self.assertNotIn(
            "secret",
            str(error.exception),
        )


    def test_connection_failure_is_sanitized(
        self,
    ):
        class FakeConnectionError(Exception):
            pass

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    side_effect=(
                        FakeConnectionError(
                            "provider connection detail secret"
                        )
                    )
                )
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with patch(
            (
                "ai_services.providers.openai_text."
                "APIConnectionError"
            ),
            FakeConnectionError,
        ):
            with self.assertRaises(
                AIProviderUnavailableError
            ) as error:
                provider.generate(
                    prompt_package=(
                        build_career_match_explanation_prompt(
                            self.recommendation()
                        )
                    ),
                    output_model=(
                        CareerMatchExplanation
                    ),
                )

        self.assertEqual(
            str(error.exception),
            (
                "OpenAI text-generation service "
                "is currently unavailable."
            ),
        )

        self.assertNotIn(
            "secret",
            str(error.exception),
        )


    def test_rate_limit_failure_is_sanitized(
        self,
    ):
        class FakeRateLimitError(Exception):
            pass

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    side_effect=(
                        FakeRateLimitError(
                            "provider rate-limit detail secret"
                        )
                    )
                )
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with patch(
            (
                "ai_services.providers.openai_text."
                "RateLimitError"
            ),
            FakeRateLimitError,
        ):
            with self.assertRaises(
                AIProviderUnavailableError
            ) as error:
                provider.generate(
                    prompt_package=(
                        build_career_match_explanation_prompt(
                            self.recommendation()
                        )
                    ),
                    output_model=(
                        CareerMatchExplanation
                    ),
                )

        self.assertEqual(
            str(error.exception),
            (
                "OpenAI text-generation service "
                "is currently unavailable."
            ),
        )

        self.assertNotIn(
            "secret",
            str(error.exception),
        )


    def test_api_status_failure_exposes_only_status_code(
        self,
    ):
        class FakeStatusError(Exception):
            def __init__(
                self,
                message,
                status_code,
            ):
                super().__init__(
                    message
                )
                self.status_code = (
                    status_code
                )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    side_effect=(
                        FakeStatusError(
                            "provider response body secret",
                            500,
                        )
                    )
                )
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with patch(
            (
                "ai_services.providers.openai_text."
                "APIStatusError"
            ),
            FakeStatusError,
        ):
            with self.assertRaises(
                AIProviderError
            ) as error:
                provider.generate(
                    prompt_package=(
                        build_career_match_explanation_prompt(
                            self.recommendation()
                        )
                    ),
                    output_model=(
                        CareerMatchExplanation
                    ),
                )

        self.assertEqual(
            str(error.exception),
            (
                "OpenAI text-generation request "
                "failed with HTTP 500."
            ),
        )

        self.assertNotIn(
            "secret",
            str(error.exception),
        )


    def test_unexpected_provider_failure_is_sanitized(
        self,
    ):
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    side_effect=RuntimeError(
                        "unexpected provider detail secret"
                    )
                )
            )
        )

        provider = OpenAITextProvider(
            model="gpt-test",
            client=client,
        )

        with self.assertRaises(
            AIProviderError
        ) as error:
            provider.generate(
                prompt_package=(
                    build_career_match_explanation_prompt(
                        self.recommendation()
                    )
                ),
                output_model=(
                    CareerMatchExplanation
                ),
            )

        self.assertEqual(
            str(error.exception),
            (
                "Unexpected OpenAI text-generation "
                "provider failure."
            ),
        )

        self.assertNotIn(
            "secret",
            str(error.exception),
        )
