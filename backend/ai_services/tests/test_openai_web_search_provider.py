import json
import os
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

from pydantic import ValidationError

from ai_services.exceptions import (
    AIInputError,
    AIProviderError,
    AIProviderUnavailableError,
    AIResponseValidationError,
)
from ai_services.prompts.learning_resource_discovery import (
    build_learning_resource_discovery_prompt,
)
from ai_services.providers.openai_web_search import (
    DEFAULT_WEB_SEARCH_MODEL,
    OpenAIWebSearchProvider,
    _sanitize_schema,
    resolve_web_search_model,
)
from ai_services.schemas.inputs import (
    LearningResourceDiscoveryInput,
)
from ai_services.schemas.outputs import (
    LearningResourceDiscoveryResult,
)


class OpenAIWebSearchProviderTests(
    TestCase
):
    def prompt(
        self,
    ):
        return (
            build_learning_resource_discovery_prompt(
                LearningResourceDiscoveryInput(
                    skill_name=(
                        "Mathematics Knowledge"
                    ),
                    skill_description=(
                        "Knowledge of arithmetic, algebra, "
                        "geometry, calculus, statistics, "
                        "and their applications."
                    ),
                    career_name=(
                        "Software Engineer"
                    ),
                    access_type="free",
                    requested_count=2,
                    existing_urls=[],
                )
            )
        )


    def valid_payload(
        self,
    ):
        return {
            "candidates": [
                {
                    "title": (
                        "Example Mathematics Course"
                    ),
                    "provider": (
                        "Example University"
                    ),
                    "url": (
                        "https://example.edu/"
                        "mathematics"
                    ),
                    "resource_type": (
                        "course"
                    ),
                    "access_type": (
                        "free"
                    ),
                    "description": (
                        "Mathematics learning resource."
                    ),
                }
            ],
            "is_ai_generated": True,
        }


    def response(
        self,
        *,
        include_web_search=True,
    ):
        output = []

        if include_web_search:
            output.append(
                SimpleNamespace(
                    type=(
                        "web_search_call"
                    ),
                    action=(
                        SimpleNamespace(
                            type="search",
                            sources=[
                                SimpleNamespace(
                                    url=(
                                        "https://example.edu/"
                                        "mathematics"
                                    )
                                ),
                                SimpleNamespace(
                                    url=(
                                        "https://example.org/"
                                        "supporting-source"
                                    )
                                ),
                            ],
                        )
                    ),
                )
            )

        output.append(
            SimpleNamespace(
                type="message",
                content=[
                    SimpleNamespace(
                        type="output_text",
                        annotations=[
                            SimpleNamespace(
                                type="url_citation",
                                url=(
                                    "https://example.edu/"
                                    "mathematics"
                                ),
                                title=(
                                    "Example Mathematics Course"
                                ),
                            )
                        ],
                    )
                ],
            )
        )

        return SimpleNamespace(
            output_text=(
                json.dumps(
                    self.valid_payload()
                )
            ),
            output=output,
            usage=SimpleNamespace(
                input_tokens=150,
                output_tokens=80,
                total_tokens=230,
            ),
        )



    def test_schema_sanitizer_preserves_application_title_field(
        self,
    ):
        raw_schema = (
            LearningResourceDiscoveryResult
            .model_json_schema()
        )

        schema = (
            _sanitize_schema(
                raw_schema
            )
        )

        candidate_schema = (
            schema[
                "$defs"
            ][
                "DiscoveredLearningResourceCandidate"
            ]
        )

        properties = (
            candidate_schema[
                "properties"
            ]
        )

        required = (
            candidate_schema[
                "required"
            ]
        )

        self.assertIn(
            "title",
            properties,
        )

        self.assertIn(
            "title",
            required,
        )

        self.assertEqual(
            set(
                required
            ),
            set(
                properties.keys()
            ),
        )

        self.assertNotIn(
            "title",
            schema,
        )


    def test_default_model_is_web_search_model(
        self,
    ):
        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            self.assertEqual(
                resolve_web_search_model(),
                DEFAULT_WEB_SEARCH_MODEL,
            )


    def test_environment_model_override(
        self,
    ):
        with patch.dict(
            os.environ,
            {
                "OPENAI_WEB_SEARCH_MODEL": (
                    "custom-search-model"
                )
            },
            clear=True,
        ):
            self.assertEqual(
                resolve_web_search_model(),
                "custom-search-model",
            )


    def test_explicit_model_overrides_environment(
        self,
    ):
        with patch.dict(
            os.environ,
            {
                "OPENAI_WEB_SEARCH_MODEL": (
                    "environment-model"
                )
            },
            clear=True,
        ):
            self.assertEqual(
                resolve_web_search_model(
                    "explicit-model"
                ),
                "explicit-model",
            )


    def test_blank_explicit_model_is_rejected(
        self,
    ):
        with self.assertRaises(
            AIInputError
        ):
            resolve_web_search_model(
                "   "
            )


    def test_missing_api_key_is_rejected(
        self,
    ):
        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            with self.assertRaises(
                AIProviderUnavailableError
            ):
                OpenAIWebSearchProvider()


    def test_generate_uses_required_web_search_and_schema(
        self,
    ):
        response = self.response()

        create_mock = Mock(
            return_value=response
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=create_mock
            )
        )

        provider = (
            OpenAIWebSearchProvider(
                model="gpt-test",
                client=client,
            )
        )

        result = provider.generate(
            prompt_package=(
                self.prompt()
            ),
            output_model=(
                LearningResourceDiscoveryResult
            ),
        )

        self.assertIsInstance(
            result,
            LearningResourceDiscoveryResult,
        )

        kwargs = (
            create_mock
            .call_args
            .kwargs
        )

        self.assertEqual(
            kwargs[
                "model"
            ],
            "gpt-test",
        )

        self.assertEqual(
            kwargs[
                "tools"
            ],
            [
                {
                    "type": (
                        "web_search"
                    )
                }
            ],
        )

        self.assertEqual(
            kwargs[
                "tool_choice"
            ],
            "required",
        )

        self.assertEqual(
            kwargs[
                "include"
            ],
            [
                (
                    "web_search_call."
                    "action.sources"
                )
            ],
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
            "low",
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


    def test_generate_extracts_unique_source_urls(
        self,
    ):
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=(
                        self.response()
                    )
                )
            )
        )

        provider = (
            OpenAIWebSearchProvider(
                model="gpt-test",
                client=client,
            )
        )

        provider.generate(
            prompt_package=(
                self.prompt()
            ),
            output_model=(
                LearningResourceDiscoveryResult
            ),
        )

        self.assertTrue(
            provider.web_search_used
        )

        self.assertEqual(
            provider.last_source_urls,
            (
                (
                    "https://example.edu/"
                    "mathematics"
                ),
                (
                    "https://example.org/"
                    "supporting-source"
                ),
            ),
        )



    def test_generate_tracks_web_search_call_count(
        self,
    ):
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=(
                        self.response()
                    )
                )
            )
        )

        provider = (
            OpenAIWebSearchProvider(
                model="gpt-test",
                client=client,
            )
        )

        provider.generate(
            prompt_package=(
                self.prompt()
            ),
            output_model=(
                LearningResourceDiscoveryResult
            ),
        )

        self.assertEqual(
            provider.last_web_search_call_count,
            1,
        )


    def test_generate_tracks_usage(
        self,
    ):
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=(
                        self.response()
                    )
                )
            )
        )

        provider = (
            OpenAIWebSearchProvider(
                model="gpt-test",
                client=client,
            )
        )

        provider.generate(
            prompt_package=(
                self.prompt()
            ),
            output_model=(
                LearningResourceDiscoveryResult
            ),
        )

        self.assertEqual(
            provider.last_usage[
                "total_tokens"
            ],
            230,
        )


    def test_generate_rejects_response_without_web_search_call(
        self,
    ):
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=(
                        self.response(
                            include_web_search=False
                        )
                    )
                )
            )
        )

        provider = (
            OpenAIWebSearchProvider(
                model="gpt-test",
                client=client,
            )
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            provider.generate(
                prompt_package=(
                    self.prompt()
                ),
                output_model=(
                    LearningResourceDiscoveryResult
                ),
            )


    def test_generate_rejects_invalid_structured_output(
        self,
    ):
        response = self.response()

        response.output_text = (
            json.dumps(
                {
                    "candidates": [
                        {
                            "title": (
                                "Invalid"
                            ),
                            "provider": (
                                "Example"
                            ),
                            "url": (
                                "ftp://example.com/"
                                "invalid"
                            ),
                            "resource_type": (
                                "course"
                            ),
                            "access_type": (
                                "free"
                            ),
                            "description": (
                                "Invalid URL."
                            ),
                        }
                    ],
                    "is_ai_generated": True,
                }
            )
        )

        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    return_value=response
                )
            )
        )

        provider = (
            OpenAIWebSearchProvider(
                model="gpt-test",
                client=client,
            )
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            provider.generate(
                prompt_package=(
                    self.prompt()
                ),
                output_model=(
                    LearningResourceDiscoveryResult
                ),
            )


    def test_unexpected_provider_error_is_translated(
        self,
    ):
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=Mock(
                    side_effect=(
                        RuntimeError(
                            "Unexpected failure."
                        )
                    )
                )
            )
        )

        provider = (
            OpenAIWebSearchProvider(
                model="gpt-test",
                client=client,
            )
        )

        with self.assertRaises(
            AIProviderError
        ):
            provider.generate(
                prompt_package=(
                    self.prompt()
                ),
                output_model=(
                    LearningResourceDiscoveryResult
                ),
            )
