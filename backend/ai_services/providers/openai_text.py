"""
OpenAI text-generation provider for GradNavi.

Uses the Responses API.

This provider is initially used for the short Career Match explanation.
"""

import os
import re
from typing import (
    Any,
    TypeVar,
)

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)
from pydantic import (
    BaseModel,
    ValidationError as PydanticValidationError,
)

from ai_services.exceptions import (
    AIInputError,
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIResponseValidationError,
)
from ai_services.prompts.common import (
    PromptPackage,
)


OutputModelT = TypeVar(
    "OutputModelT",
    bound=BaseModel,
)


DEFAULT_TEXT_MODEL = (
    "gpt-5-nano"
)

DEFAULT_TIMEOUT_SECONDS = 30.0

MAX_OUTPUT_TOKENS = 500


def resolve_text_model(
    model: str | None = None,
) -> str:
    resolved = (
        model
        or os.getenv(
            "OPENAI_TEXT_MODEL"
        )
        or DEFAULT_TEXT_MODEL
    )

    value = (
        resolved.strip()
    )

    if not value:
        raise AIInputError(
            "Text-generation model must not be blank."
        )

    return value


def _sanitize_schema(
    value,
):
    """
    Keep the strict Structured Outputs schema conservative.

    Pydantic performs the complete application validation after generation.
    """

    if isinstance(
        value,
        list,
    ):
        return [
            _sanitize_schema(
                item
            )
            for item
            in value
        ]

    if not isinstance(
        value,
        dict,
    ):
        return value

    cleaned = {}

    unsupported_keywords = {
        "title",
        "default",
        "examples",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
    }

    for key, item in value.items():

        if key in unsupported_keywords:
            continue

        if key == "const":
            cleaned[
                "enum"
            ] = [
                item
            ]
            continue

        cleaned[
            key
        ] = (
            _sanitize_schema(
                item
            )
        )

    return cleaned


class OpenAITextProvider:
    """
    OpenAI implementation of the GradNavi AIProvider generation contract.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = (
            DEFAULT_TIMEOUT_SECONDS
        ),
        client: Any | None = None,
    ):
        if timeout_seconds <= 0:
            raise AIInputError(
                "Text-generation timeout must be greater than zero."
            )

        self.model = (
            resolve_text_model(
                model
            )
        )

        self.timeout_seconds = (
            timeout_seconds
        )

        self.last_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

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
            api_key=(
                resolved_api_key
            ),
            timeout=(
                timeout_seconds
            ),
            max_retries=2,
        )


    def generate(
        self,
        *,
        prompt_package: PromptPackage,
        output_model: type[OutputModelT],
    ) -> OutputModelT:
        """
        Generate and validate one structured GradNavi AI result.
        """

        instructions = (
            "\n".join(
                (
                    *prompt_package
                    .system_instructions,

                    *prompt_package
                    .safety_rules,

                    *prompt_package
                    .output_requirements,
                )
            )
        )

        model_input = (
            "OPERATION\n"
            f"{prompt_package.operation.value}"
            "\n\nTRUSTED STRUCTURED CONTEXT\n"
            f"{prompt_package.trusted_context}"
            "\n\nUNTRUSTED USER CONTENT\n"
            f"{prompt_package.untrusted_content}"
        )

        schema_name = re.sub(
            r"[^A-Za-z0-9_-]",
            "_",
            output_model.__name__,
        )[:64]

        schema = (
            _sanitize_schema(
                output_model
                .model_json_schema()
            )
        )

        try:
            response = (
                self._client
                .responses
                .create(
                    model=(
                        self.model
                    ),
                    instructions=(
                        instructions
                    ),
                    input=(
                        model_input
                    ),
                    store=False,
                    reasoning={
                        "effort": "minimal",
                    },
                    max_output_tokens=(
                        MAX_OUTPUT_TOKENS
                    ),
                    text={
                        "verbosity": "low",
                        "format": {
                            "type": (
                                "json_schema"
                            ),
                            "name": (
                                schema_name
                            ),
                            "schema": (
                                schema
                            ),
                            "strict": True,
                        },
                    },
                )
            )

        except APITimeoutError as error:
            raise AIProviderTimeoutError(
                "OpenAI text-generation request timed out."
            ) from error

        except (
            APIConnectionError,
            RateLimitError,
        ) as error:
            raise AIProviderUnavailableError(
                "OpenAI text-generation service is currently unavailable."
            ) from error

        except APIStatusError as error:
            status_code = getattr(
                error,
                "status_code",
                None,
            )

            message = (
                "OpenAI text-generation request failed"
            )

            if status_code is not None:
                message += (
                    f" with HTTP {status_code}."
                )
            else:
                message += "."

            raise AIProviderError(
                message
            ) from error

        except Exception as error:
            raise AIProviderError(
                "Unexpected OpenAI text-generation provider failure."
            ) from error

        usage = getattr(
            response,
            "usage",
            None,
        )

        if usage is not None:
            self.last_usage = {
                "input_tokens": (
                    getattr(
                        usage,
                        "input_tokens",
                        0,
                    )
                    or 0
                ),
                "output_tokens": (
                    getattr(
                        usage,
                        "output_tokens",
                        0,
                    )
                    or 0
                ),
                "total_tokens": (
                    getattr(
                        usage,
                        "total_tokens",
                        0,
                    )
                    or 0
                ),
            }

        output_text = getattr(
            response,
            "output_text",
            None,
        )

        if (
            not isinstance(
                output_text,
                str,
            )
            or not output_text.strip()
        ):
            raise AIResponseValidationError(
                "OpenAI response did not contain structured output text."
            )

        try:
            return (
                output_model
                .model_validate_json(
                    output_text
                )
            )

        except PydanticValidationError as error:
            raise AIResponseValidationError(
                "OpenAI structured output failed GradNavi validation."
            ) from error
