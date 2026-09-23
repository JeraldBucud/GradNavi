"""
OpenAI web-search provider for GradNavi Learning Resource discovery.

This provider uses the Responses API hosted web_search tool.

The provider is isolated from normal GradNavi text generation so
web-enabled operations do not change Resume, Cover Letter, Interview,
Career Match, Skill Gap, Roadmap, or Learning Resource guidance calls.
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


DEFAULT_WEB_SEARCH_MODEL = (
    "gpt-5.4-nano"
)

DEFAULT_WEB_SEARCH_TIMEOUT_SECONDS = 45.0

MAX_WEB_SEARCH_OUTPUT_TOKENS = 2_500


def resolve_web_search_model(
    model: str | None = None,
) -> str:
    resolved = (
        model
        or os.getenv(
            "OPENAI_WEB_SEARCH_MODEL"
        )
        or DEFAULT_WEB_SEARCH_MODEL
    )

    value = (
        resolved.strip()
    )

    if not value:
        raise AIInputError(
            "Web-search model must not be blank."
        )

    return value


def _sanitize_schema(
    value,
    *,
    in_properties: bool = False,
):
    """
    Keep the Structured Outputs schema conservative.

    JSON Schema metadata keys such as title are removed from
    schema objects, but real application field names inside a
    properties mapping must be preserved.

    Full application validation still runs through Pydantic
    after the provider response is returned.
    """

    if isinstance(
        value,
        list,
    ):
        return [
            _sanitize_schema(
                item,
                in_properties=False,
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

        if in_properties:
            cleaned[
                key
            ] = (
                _sanitize_schema(
                    item,
                    in_properties=False,
                )
            )

            continue

        if key == "properties":
            cleaned[
                key
            ] = (
                _sanitize_schema(
                    item,
                    in_properties=True,
                )
            )

            continue

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
                item,
                in_properties=False,
            )
        )

    return cleaned


def _field(
    value,
    name,
    default=None,
):
    if isinstance(
        value,
        dict,
    ):
        return value.get(
            name,
            default,
        )

    return getattr(
        value,
        name,
        default,
    )


def _items(
    value,
):
    if value is None:
        return ()

    if isinstance(
        value,
        (
            list,
            tuple,
        ),
    ):
        return value

    try:
        return tuple(
            value
        )
    except TypeError:
        return ()


def _extract_web_search_metadata(
    response,
) -> tuple[
    bool,
    tuple[str, ...],
    int,
]:
    """
    Extract whether web search ran and every source URL returned
    through the Responses API search metadata or URL citations.
    """

    web_search_used = False

    web_search_call_count = 0

    urls = []

    for item in _items(
        _field(
            response,
            "output",
            (),
        )
    ):
        item_type = _field(
            item,
            "type",
            "",
        )

        if item_type == "web_search_call":
            web_search_used = True

            web_search_call_count += 1

            action = _field(
                item,
                "action",
                None,
            )

            for source in _items(
                _field(
                    action,
                    "sources",
                    (),
                )
            ):
                url = str(
                    _field(
                        source,
                        "url",
                        "",
                    )
                    or ""
                ).strip()

                if url:
                    urls.append(
                        url
                    )

        if item_type != "message":
            continue

        for content in _items(
            _field(
                item,
                "content",
                (),
            )
        ):
            for annotation in _items(
                _field(
                    content,
                    "annotations",
                    (),
                )
            ):
                if (
                    _field(
                        annotation,
                        "type",
                        "",
                    )
                    != "url_citation"
                ):
                    continue

                url = str(
                    _field(
                        annotation,
                        "url",
                        "",
                    )
                    or ""
                ).strip()

                if url:
                    urls.append(
                        url
                    )

    unique_urls = tuple(
        dict.fromkeys(
            urls
        )
    )

    return (
        web_search_used,
        unique_urls,
        web_search_call_count,
    )


class OpenAIWebSearchProvider:
    """
    OpenAI Responses API provider with mandatory hosted web search.

    This provider is intended for externally grounded discovery
    operations such as Learning Resource discovery.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float = (
            DEFAULT_WEB_SEARCH_TIMEOUT_SECONDS
        ),
        client: Any | None = None,
    ):
        if timeout_seconds <= 0:
            raise AIInputError(
                "Web-search timeout must be greater than zero."
            )

        self.model = (
            resolve_web_search_model(
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

        self.last_source_urls = ()

        self.web_search_used = False

        self.last_web_search_call_count = 0

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
        Run mandatory web search and validate structured output.
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

        self.last_source_urls = ()
        self.web_search_used = False
        self.last_web_search_call_count = 0

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
                        "effort": "low",
                    },
                    tools=[
                        {
                            "type": (
                                "web_search"
                            ),
                        }
                    ],
                    tool_choice=(
                        "required"
                    ),
                    include=[
                        (
                            "web_search_call."
                            "action.sources"
                        )
                    ],
                    max_output_tokens=(
                        MAX_WEB_SEARCH_OUTPUT_TOKENS
                    ),
                    text={
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
                "OpenAI web-search request timed out."
            ) from error

        except (
            APIConnectionError,
            RateLimitError,
        ) as error:
            raise AIProviderUnavailableError(
                "OpenAI web-search service is currently unavailable."
            ) from error

        except APIStatusError as error:
            status_code = getattr(
                error,
                "status_code",
                None,
            )

            message = (
                "OpenAI web-search request failed"
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
                "Unexpected OpenAI web-search provider failure."
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

        (
            self.web_search_used,
            self.last_source_urls,
            self.last_web_search_call_count,
        ) = (
            _extract_web_search_metadata(
                response
            )
        )

        if not self.web_search_used:
            raise AIResponseValidationError(
                "OpenAI response did not contain a web-search call."
            )

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
                "OpenAI web-search response did not contain "
                "structured output text."
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
                "OpenAI web-search structured output failed "
                "GradNavi validation."
            ) from error
