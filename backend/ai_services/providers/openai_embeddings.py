"""
OpenAI embedding provider for GradNavi.

This module is the provider-specific implementation behind the
provider-independent EmbeddingProvider contract.

Current GradNavi semantic-alignment model:

    text-embedding-3-small

Privacy filtering must happen before text reaches this provider.
This provider receives prepared text only.

The API key is never printed or returned.
"""

import os

from collections.abc import Sequence
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

from ai_services.exceptions import (
    AIInputError,
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIResponseValidationError,
)

from ai_services.providers.embeddings import (
    EmbeddingBatchResult,
)


DEFAULT_EMBEDDING_MODEL = (
    "text-embedding-3-small"
)

DEFAULT_TIMEOUT_SECONDS = 30.0


class OpenAIEmbeddingProvider:
    """
    Concrete OpenAI implementation of GradNavi embeddings.

    client
        Optional injected client used by automated tests.

    api_key
        Optional explicit API key. When omitted, OPENAI_API_KEY
        is read from the environment.

    model
        Embedding model identifier.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_EMBEDDING_MODEL,
        timeout_seconds: float = (
            DEFAULT_TIMEOUT_SECONDS
        ),
        client: Any | None = None,
    ):
        if not model.strip():
            raise AIInputError(
                "Embedding model must not be blank."
            )

        if timeout_seconds <= 0:
            raise AIInputError(
                "Embedding timeout must be greater "
                "than zero."
            )

        self.model = model.strip()

        self.timeout_seconds = (
            timeout_seconds
        )

        if client is not None:
            self._client = client
            return

        resolved_api_key = (
            api_key
            or os.getenv(
                "OPENAI_API_KEY"
            )
        )

        if not resolved_api_key:
            raise AIProviderUnavailableError(
                "OPENAI_API_KEY is not configured."
            )

        self._client = OpenAI(
            api_key=resolved_api_key,
            timeout=timeout_seconds,
            max_retries=2,
        )

    def embed_texts(
        self,
        *,
        texts: Sequence[str],
    ) -> EmbeddingBatchResult:
        """
        Embed a batch of texts and preserve input order.
        """

        normalized_texts = self._validate_texts(
            texts
        )

        try:
            response = (
                self._client
                .embeddings
                .create(
                    model=self.model,
                    input=list(
                        normalized_texts
                    ),
                )
            )

        except APITimeoutError as error:
            raise AIProviderTimeoutError(
                "OpenAI embedding request timed out."
            ) from error

        except (
            APIConnectionError,
            RateLimitError,
        ) as error:
            raise AIProviderUnavailableError(
                "OpenAI embedding service is "
                "currently unavailable."
            ) from error

        except APIStatusError as error:
            status_code = getattr(
                error,
                "status_code",
                None,
            )

            raise AIProviderError(
                "OpenAI embedding request failed"
                + (
                    f" with HTTP {status_code}."
                    if status_code
                    is not None
                    else "."
                )
            ) from error

        except Exception as error:
            raise AIProviderError(
                "Unexpected OpenAI embedding "
                "provider failure."
            ) from error

        return self._normalize_response(
            response=response,
            expected_count=len(
                normalized_texts
            ),
        )

    def _validate_texts(
        self,
        texts: Sequence[str],
    ) -> tuple[str, ...]:
        """
        Validate application input before provider execution.
        """

        if isinstance(
            texts,
            (
                str,
                bytes,
            ),
        ):
            raise AIInputError(
                "texts must be a sequence of strings, "
                "not one string value."
            )

        normalized = []

        for index, text in enumerate(
            texts
        ):
            if not isinstance(
                text,
                str,
            ):
                raise AIInputError(
                    "Embedding input at index "
                    f"{index} must be a string."
                )

            value = text.strip()

            if not value:
                raise AIInputError(
                    "Embedding input at index "
                    f"{index} must not be blank."
                )

            normalized.append(
                value
            )

        if not normalized:
            raise AIInputError(
                "At least one embedding input "
                "is required."
            )

        return tuple(
            normalized
        )

    def _normalize_response(
        self,
        *,
        response: Any,
        expected_count: int,
    ) -> EmbeddingBatchResult:
        """
        Convert provider output to GradNavi's normalized contract.
        """

        data = getattr(
            response,
            "data",
            None,
        )

        if not isinstance(
            data,
            list,
        ):
            raise AIResponseValidationError(
                "Embedding response does not contain "
                "a valid data list."
            )

        if len(data) != expected_count:
            raise AIResponseValidationError(
                "Embedding response count does not "
                "match input count."
            )

        try:
            ordered_items = sorted(
                data,
                key=lambda item: item.index,
            )

        except (
            AttributeError,
            TypeError,
        ) as error:
            raise AIResponseValidationError(
                "Embedding response indexes are invalid."
            ) from error

        expected_indexes = list(
            range(
                expected_count
            )
        )

        actual_indexes = [
            item.index
            for item
            in ordered_items
        ]

        if (
            actual_indexes
            != expected_indexes
        ):
            raise AIResponseValidationError(
                "Embedding response indexes do not "
                "match input order."
            )

        vectors = []

        dimensions = None

        for item in ordered_items:
            raw_vector = getattr(
                item,
                "embedding",
                None,
            )

            if not isinstance(
                raw_vector,
                list,
            ):
                raise AIResponseValidationError(
                    "Embedding response contains an "
                    "invalid vector."
                )

            if not raw_vector:
                raise AIResponseValidationError(
                    "Embedding response contains an "
                    "empty vector."
                )

            try:
                vector = tuple(
                    float(
                        value
                    )
                    for value
                    in raw_vector
                )

            except (
                TypeError,
                ValueError,
            ) as error:
                raise AIResponseValidationError(
                    "Embedding response contains a "
                    "non-numeric vector value."
                ) from error

            if dimensions is None:
                dimensions = len(
                    vector
                )

            elif (
                len(
                    vector
                )
                != dimensions
            ):
                raise AIResponseValidationError(
                    "Embedding vectors have inconsistent "
                    "dimensions."
                )

            vectors.append(
                vector
            )

        usage = getattr(
            response,
            "usage",
            None,
        )

        if usage is None:
            raise AIResponseValidationError(
                "Embedding response is missing usage data."
            )

        prompt_tokens = getattr(
            usage,
            "prompt_tokens",
            None,
        )

        total_tokens = getattr(
            usage,
            "total_tokens",
            None,
        )

        if (
            not isinstance(
                prompt_tokens,
                int,
            )
            or prompt_tokens < 0
        ):
            raise AIResponseValidationError(
                "Embedding prompt-token usage is invalid."
            )

        if (
            not isinstance(
                total_tokens,
                int,
            )
            or total_tokens < 0
        ):
            raise AIResponseValidationError(
                "Embedding total-token usage is invalid."
            )

        returned_model = getattr(
            response,
            "model",
            None,
        )

        if (
            not isinstance(
                returned_model,
                str,
            )
            or not returned_model.strip()
        ):
            raise AIResponseValidationError(
                "Embedding response model is invalid."
            )

        return EmbeddingBatchResult(
            vectors=tuple(
                vectors
            ),
            model=returned_model,
            prompt_tokens=prompt_tokens,
            total_tokens=total_tokens,
        )
