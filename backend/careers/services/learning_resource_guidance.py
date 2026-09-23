"""
Personalised Learning Resource AI guidance.

Resource selection and ranking remain deterministic.

Only the first six ranked resources receive AI-written
personalisation.

Resources outside the first six continue using their
deterministic fallback explanation.
"""

import hashlib
import json
from collections.abc import (
    Mapping,
)

from ai_services.exceptions import (
    AIProviderError,
    AIResponseValidationError,
)
from ai_services.prompts.learning_resource_guidance import (
    build_learning_resource_guidance_prompt,
)
from ai_services.safety.privacy import (
    build_student_profile_context,
)
from ai_services.schemas.outputs import (
    LearningResourceGuidanceExplanation,
)
from careers.models import (
    LearningResourceGuidanceSnapshot,
)


LEARNING_RESOURCE_GUIDANCE_VERSION = (
    "learning_resource_guidance_v1"
)

MAX_AI_RESOURCES = 6


def build_learning_resource_guidance_source(
    *,
    career_id: int,
    career_name: str,
    skill_id: int,
    skill_name: str,
    resources,
) -> dict:
    """
    Build the deterministic source used for generation
    and cache invalidation.

    Only the first six ranked resources enter the AI layer.
    """

    selected = tuple(
        resources
    )[
        :MAX_AI_RESOURCES
    ]

    return {
        "career_id": (
            int(
                career_id
            )
        ),
        "career_name": (
            str(
                career_name
            ).strip()
        ),
        "skill_id": (
            int(
                skill_id
            )
        ),
        "skill_name": (
            str(
                skill_name
            ).strip()
        ),
        "resources": [
            {
                "resource_id": (
                    resource.id
                ),
                "title": (
                    resource.title
                ),
                "provider": (
                    resource.provider
                ),
                "resource_type": (
                    resource.resource_type
                ),
                "access_type": (
                    resource.access_type
                ),
                "description": (
                    resource.description
                ),
                "helpful_count": (
                    resource.helpful_count
                ),
                "not_helpful_count": (
                    resource.not_helpful_count
                ),
                "feedback_score": (
                    resource.feedback_score
                ),
                "last_verified_at": (
                    resource
                    .last_verified_at
                    .isoformat()
                    if resource
                    .last_verified_at
                    is not None
                    else None
                ),
                "fallback_explanation": (
                    resource
                    .why_this_fits
                ),
            }
            for resource
            in selected
        ],
    }


def build_learning_resource_guidance_cache_key(
    *,
    profile_context,
    source: Mapping[
        str,
        object,
    ],
    model: str,
) -> str:

    fingerprint = {
        "version": (
            LEARNING_RESOURCE_GUIDANCE_VERSION
        ),
        "model": model,
        "profile": (
            profile_context.model_dump(
                mode="json"
            )
        ),
        "source": dict(
            source
        ),
    }

    serialized = json.dumps(
        fingerprint,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        default=str,
    )

    return hashlib.sha256(
        serialized.encode(
            "utf-8"
        )
    ).hexdigest()


def align_resource_guidance(
    *,
    guidance_items,
    resources,
):
    """
    Enforce the exact deterministic resource set and order.
    """

    expected = list(
        resources
    )

    if (
        len(
            guidance_items
        )
        != len(
            expected
        )
    ):
        raise AIResponseValidationError(
            "Learning Resource AI guidance count "
            "does not match deterministic resource count."
        )

    by_id = {}

    for item in guidance_items:

        resource_id = (
            int(
                item.resource_id
            )
        )

        if resource_id in by_id:
            raise AIResponseValidationError(
                "Learning Resource AI guidance "
                "contains a duplicate resource."
            )

        by_id[
            resource_id
        ] = item

    aligned = []

    for resource in expected:

        resource_id = int(
            resource.get(
                "resource_id"
            )
        )

        if resource_id not in by_id:
            raise AIResponseValidationError(
                "Learning Resource AI guidance "
                "does not match deterministic "
                f"resource {resource_id}."
            )

        item = by_id[
            resource_id
        ]

        aligned.append(
            {
                "resource_id": (
                    resource_id
                ),
                "title": (
                    resource.get(
                        "title"
                    )
                ),
                "why_this_fits": (
                    item
                    .why_this_fits
                    .strip()
                ),
            }
        )

    return aligned


def build_fallback_resource_guidance(
    source,
):
    """
    Return existing deterministic explanations.
    """

    return [
        {
            "resource_id": (
                resource.get(
                    "resource_id"
                )
            ),
            "title": (
                resource.get(
                    "title"
                )
            ),
            "why_this_fits": (
                resource.get(
                    "fallback_explanation"
                )
            ),
        }
        for resource
        in source.get(
            "resources",
            []
        )
    ]


def generate_learning_resource_guidance(
    *,
    profile_context,
    source,
    provider,
):

    resources = list(
        source.get(
            "resources",
            []
        )
    )

    if not resources:
        return []

    prompt_package = (
        build_learning_resource_guidance_prompt(
            profile=profile_context,
            resource_context=source,
        )
    )

    result = provider.generate(
        prompt_package=(
            prompt_package
        ),
        output_model=(
            LearningResourceGuidanceExplanation
        ),
    )

    return align_resource_guidance(
        guidance_items=(
            result.guidance_items
        ),
        resources=resources,
    )


def get_cached_learning_resource_guidance(
    *,
    student_profile_id: int,
    career_id: int,
    skill_id: int,
    cache_key: str,
    model: str,
):
    return (
        LearningResourceGuidanceSnapshot
        .objects
        .filter(
            student_profile_id=(
                student_profile_id
            ),
            career_id=career_id,
            skill_id=skill_id,
            cache_key=cache_key,
            guidance_version=(
                LEARNING_RESOURCE_GUIDANCE_VERSION
            ),
            model=model,
        )
        .first()
    )


def store_learning_resource_guidance(
    *,
    student_profile_id: int,
    career_id: int,
    skill_id: int,
    cache_key: str,
    model: str,
    payload,
    prompt_tokens: int = 0,
    total_tokens: int = 0,
):
    snapshot, _ = (
        LearningResourceGuidanceSnapshot
        .objects
        .update_or_create(
            student_profile_id=(
                student_profile_id
            ),
            career_id=career_id,
            skill_id=skill_id,
            defaults={
                "cache_key": (
                    cache_key
                ),
                "guidance_version": (
                    LEARNING_RESOURCE_GUIDANCE_VERSION
                ),
                "model": model,
                "payload": dict(
                    payload
                ),
                "prompt_tokens": (
                    max(
                        int(
                            prompt_tokens
                            or 0
                        ),
                        0,
                    )
                ),
                "total_tokens": (
                    max(
                        int(
                            total_tokens
                            or 0
                        ),
                        0,
                    )
                ),
            },
        )
    )

    return snapshot


def get_or_generate_learning_resource_guidance(
    *,
    student_profile,
    career_id: int,
    career_name: str,
    skill_id: int,
    skill_name: str,
    ranked_resources,
    provider,
    model: str,
):
    """
    Cache-first Learning Resource personalisation.

    One provider request covers up to six resources.
    """

    profile_context = (
        build_student_profile_context(
            student_profile=(
                student_profile
            )
        )
    )

    source = (
        build_learning_resource_guidance_source(
            career_id=career_id,
            career_name=career_name,
            skill_id=skill_id,
            skill_name=skill_name,
            resources=ranked_resources,
        )
    )

    if not source[
        "resources"
    ]:
        return {
            "career_id": (
                career_id
            ),
            "career_name": (
                career_name
            ),
            "skill_id": (
                skill_id
            ),
            "skill_name": (
                skill_name
            ),
            "guidance_items": [],
            "is_ai_generated": False,
            "fallback": False,
            "model": model,
            "version": (
                LEARNING_RESOURCE_GUIDANCE_VERSION
            ),
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            },
            "cached": False,
        }

    cache_key = (
        build_learning_resource_guidance_cache_key(
            profile_context=(
                profile_context
            ),
            source=source,
            model=model,
        )
    )

    cached = (
        get_cached_learning_resource_guidance(
            student_profile_id=(
                student_profile.id
            ),
            career_id=career_id,
            skill_id=skill_id,
            cache_key=cache_key,
            model=model,
        )
    )

    if cached is not None:
        return {
            **cached.payload,
            "cached": True,
        }

    try:
        guidance_items = (
            generate_learning_resource_guidance(
                profile_context=(
                    profile_context
                ),
                source=source,
                provider=provider,
            )
        )

    except AIProviderError:

        return {
            "career_id": (
                career_id
            ),
            "career_name": (
                career_name
            ),
            "skill_id": (
                skill_id
            ),
            "skill_name": (
                skill_name
            ),
            "guidance_items": (
                build_fallback_resource_guidance(
                    source
                )
            ),
            "is_ai_generated": False,
            "fallback": True,
            "model": model,
            "version": (
                LEARNING_RESOURCE_GUIDANCE_VERSION
            ),
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            },
            "cached": False,
        }

    usage = getattr(
        provider,
        "last_usage",
        {},
    )

    payload = {
        "career_id": (
            career_id
        ),
        "career_name": (
            career_name
        ),
        "skill_id": (
            skill_id
        ),
        "skill_name": (
            skill_name
        ),
        "guidance_items": (
            guidance_items
        ),
        "is_ai_generated": True,
        "fallback": False,
        "model": model,
        "version": (
            LEARNING_RESOURCE_GUIDANCE_VERSION
        ),
        "usage": {
            "input_tokens": (
                usage.get(
                    "input_tokens",
                    0,
                )
            ),
            "output_tokens": (
                usage.get(
                    "output_tokens",
                    0,
                )
            ),
            "total_tokens": (
                usage.get(
                    "total_tokens",
                    0,
                )
            ),
        },
    }

    store_learning_resource_guidance(
        student_profile_id=(
            student_profile.id
        ),
        career_id=career_id,
        skill_id=skill_id,
        cache_key=cache_key,
        model=model,
        payload=payload,
        prompt_tokens=(
            payload[
                "usage"
            ][
                "input_tokens"
            ]
        ),
        total_tokens=(
            payload[
                "usage"
            ][
                "total_tokens"
            ]
        ),
    )

    return {
        **payload,
        "cached": False,
    }
