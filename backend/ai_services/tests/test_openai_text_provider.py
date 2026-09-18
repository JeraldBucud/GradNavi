import json
from types import (
    SimpleNamespace,
)
from unittest import (
    TestCase,
)
from unittest.mock import (
    Mock,
)

from ai_services.exceptions import (
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
