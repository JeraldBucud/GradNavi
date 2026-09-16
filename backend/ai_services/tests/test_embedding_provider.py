"""
Tests for the GradNavi embedding-provider boundary.

No external OpenAI request is made.

A fake client verifies:

- provider-independent protocol behaviour;
- batch ordering;
- normalized output;
- input validation;
- response validation;
- provider error translation.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase

from ai_services.exceptions import (
    AIInputError,
    AIResponseValidationError,
)

from ai_services.providers.embeddings import (
    EmbeddingBatchResult,
    EmbeddingProvider,
)

from ai_services.providers.openai_embeddings import (
    DEFAULT_EMBEDDING_MODEL,
    OpenAIEmbeddingProvider,
)


class FakeEmbeddings:
    """
    Minimal fake embeddings endpoint.
    """

    def __init__(
        self,
        response,
    ):
        self.response = response
        self.calls = []

    def create(
        self,
        *,
        model,
        input,
    ):
        self.calls.append(
            {
                "model": model,
                "input": input,
            }
        )

        return self.response


class FakeClient:
    """
    Minimal fake OpenAI client.
    """

    def __init__(
        self,
        response,
    ):
        self.embeddings = (
            FakeEmbeddings(
                response
            )
        )


def make_response(
    *,
    vectors=None,
    indexes=None,
):
    """
    Build a provider-like embedding response.
    """

    if vectors is None:
        vectors = [
            [
                0.1,
                0.2,
                0.3,
            ],
            [
                0.4,
                0.5,
                0.6,
            ],
        ]

    if indexes is None:
        indexes = list(
            range(
                len(
                    vectors
                )
            )
        )

    data = [
        SimpleNamespace(
            index=index,
            embedding=vector,
        )
        for index, vector
        in zip(
            indexes,
            vectors,
        )
    ]

    return SimpleNamespace(
        data=data,
        model=(
            DEFAULT_EMBEDDING_MODEL
        ),
        usage=SimpleNamespace(
            prompt_tokens=12,
            total_tokens=12,
        ),
    )


class EmbeddingProviderContractTests(
    SimpleTestCase
):
    """
    Provider-independent contract tests.
    """

    def test_valid_provider_satisfies_protocol(
        self,
    ):
        class StubProvider:
            def embed_texts(
                self,
                *,
                texts,
            ):
                return EmbeddingBatchResult(
                    vectors=(
                        (
                            1.0,
                            0.0,
                        ),
                    ),
                    model="stub",
                    prompt_tokens=1,
                    total_tokens=1,
                )

        provider = StubProvider()

        self.assertIsInstance(
            provider,
            EmbeddingProvider,
        )

    def test_embedding_contract_does_not_import_openai(
        self,
    ):
        provider_path = (
            Path(__file__)
            .resolve()
            .parents[1]
            / "providers"
            / "embeddings.py"
        )

        source = provider_path.read_text(
            encoding="utf-8"
        ).lower()

        self.assertNotIn(
            "import openai",
            source,
        )

        self.assertNotIn(
            "from openai",
            source,
        )


class OpenAIEmbeddingProviderTests(
    SimpleTestCase
):
    """
    Concrete OpenAI embedding provider tests.
    """

    def build_provider(
        self,
        *,
        response=None,
    ):
        if response is None:
            response = (
                make_response()
            )

        client = FakeClient(
            response
        )

        provider = (
            OpenAIEmbeddingProvider(
                client=client,
            )
        )

        return (
            provider,
            client,
        )

    def test_batch_embedding_preserves_input_order(
        self,
    ):
        provider, client = (
            self.build_provider()
        )

        result = provider.embed_texts(
            texts=(
                "Student context",
                "Career context",
            )
        )

        self.assertEqual(
            result.vector_count,
            2,
        )

        self.assertEqual(
            result.dimensions,
            3,
        )

        self.assertEqual(
            result.vectors,
            (
                (
                    0.1,
                    0.2,
                    0.3,
                ),
                (
                    0.4,
                    0.5,
                    0.6,
                ),
            ),
        )

        self.assertEqual(
            result.prompt_tokens,
            12,
        )

        self.assertEqual(
            result.total_tokens,
            12,
        )

        self.assertEqual(
            client.embeddings.calls,
            [
                {
                    "model":
                        DEFAULT_EMBEDDING_MODEL,

                    "input": [
                        "Student context",
                        "Career context",
                    ],
                }
            ],
        )

    def test_response_is_sorted_by_provider_index(
        self,
    ):
        response = make_response(
            vectors=[
                [
                    0.4,
                    0.5,
                ],
                [
                    0.1,
                    0.2,
                ],
            ],
            indexes=[
                1,
                0,
            ],
        )

        provider, _ = (
            self.build_provider(
                response=response
            )
        )

        result = provider.embed_texts(
            texts=(
                "First",
                "Second",
            )
        )

        self.assertEqual(
            result.vectors,
            (
                (
                    0.1,
                    0.2,
                ),
                (
                    0.4,
                    0.5,
                ),
            ),
        )

    def test_whitespace_is_removed_from_input_edges(
        self,
    ):
        response = make_response(
            vectors=[
                [
                    1.0,
                    2.0,
                ],
            ]
        )

        provider, client = (
            self.build_provider(
                response=response
            )
        )

        provider.embed_texts(
            texts=[
                "  GradNavi test  ",
            ]
        )

        self.assertEqual(
            client.embeddings.calls[0][
                "input"
            ],
            [
                "GradNavi test",
            ],
        )

    def test_empty_batch_is_rejected(
        self,
    ):
        provider, _ = (
            self.build_provider()
        )

        with self.assertRaises(
            AIInputError
        ):
            provider.embed_texts(
                texts=()
            )

    def test_single_string_is_rejected(
        self,
    ):
        provider, _ = (
            self.build_provider()
        )

        with self.assertRaises(
            AIInputError
        ):
            provider.embed_texts(
                texts="not a batch"
            )

    def test_blank_text_is_rejected(
        self,
    ):
        provider, _ = (
            self.build_provider()
        )

        with self.assertRaises(
            AIInputError
        ):
            provider.embed_texts(
                texts=[
                    " ",
                ]
            )

    def test_non_string_input_is_rejected(
        self,
    ):
        provider, _ = (
            self.build_provider()
        )

        with self.assertRaises(
            AIInputError
        ):
            provider.embed_texts(
                texts=[
                    123,
                ]
            )

    def test_missing_vector_is_rejected(
        self,
    ):
        response = make_response(
            vectors=[
                [],
            ]
        )

        provider, _ = (
            self.build_provider(
                response=response
            )
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            provider.embed_texts(
                texts=[
                    "GradNavi",
                ]
            )

    def test_mismatched_response_count_is_rejected(
        self,
    ):
        response = make_response(
            vectors=[
                [
                    0.1,
                    0.2,
                ],
            ]
        )

        provider, _ = (
            self.build_provider(
                response=response
            )
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            provider.embed_texts(
                texts=[
                    "First",
                    "Second",
                ]
            )

    def test_inconsistent_dimensions_are_rejected(
        self,
    ):
        response = make_response(
            vectors=[
                [
                    0.1,
                    0.2,
                ],
                [
                    0.3,
                ],
            ]
        )

        provider, _ = (
            self.build_provider(
                response=response
            )
        )

        with self.assertRaises(
            AIResponseValidationError
        ):
            provider.embed_texts(
                texts=[
                    "First",
                    "Second",
                ]
            )

    def test_provider_uses_default_model(
        self,
    ):
        provider, _ = (
            self.build_provider()
        )

        self.assertEqual(
            provider.model,
            "text-embedding-3-small",
        )

    def test_blank_model_is_rejected(
        self,
    ):
        with self.assertRaises(
            AIInputError
        ):
            OpenAIEmbeddingProvider(
                model=" ",
                client=Mock(),
            )

    def test_non_positive_timeout_is_rejected(
        self,
    ):
        with self.assertRaises(
            AIInputError
        ):
            OpenAIEmbeddingProvider(
                timeout_seconds=0,
                client=Mock(),
            )
