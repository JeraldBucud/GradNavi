"""
Personalised Career Roadmap AI guidance service.

Deterministic GradNavi data stays authoritative.

AI only writes Student-facing explanation text.

The service uses persistent database caching and returns
deterministic fallback guidance when the external AI provider
is unavailable.
"""

import hashlib
import json
from collections.abc import Mapping

from ai_services.exceptions import (
    AIProviderError,
    AIResponseValidationError,
)
from ai_services.prompts.roadmap_guidance import (
    build_roadmap_guidance_prompt,
)
from ai_services.safety.privacy import (
    build_student_profile_context,
)
from ai_services.schemas.outputs import (
    RoadmapGuidanceExplanation,
)
from careers.models import (
    RoadmapGuidanceSnapshot,
)


ROADMAP_GUIDANCE_VERSION = (
    "roadmap_guidance_v1"
)

MAX_GUIDANCE_STEPS = 3


def _value(
    value,
):
    return getattr(
        value,
        "value",
        value,
    )


def _decimal(
    value,
):
    if value is None:
        return None

    return str(
        value
    )


def build_roadmap_guidance_source(
    overview,
) -> dict:
    """
    Build the deterministic roadmap context supplied to AI.

    Only the highest-priority three current roadmap steps
    receive AI guidance.
    """

    steps = []

    for step in (
        overview.roadmap_steps[
            :MAX_GUIDANCE_STEPS
        ]
    ):
        steps.append(
            {
                "step_number": (
                    step.step_number
                ),
                "skill_id": (
                    step.skill_id
                ),
                "skill_name": (
                    step.skill_name
                ),
                "gap_status": (
                    _value(
                        step.gap_status
                    )
                ),
                "current_proficiency": (
                    step.current_proficiency
                ),
                "current_score": (
                    _decimal(
                        step.current_score
                    )
                ),
                "required_level": (
                    _decimal(
                        step.required_level
                    )
                ),
                "gap_amount": (
                    _decimal(
                        step.gap_amount
                    )
                ),
                "importance": (
                    _decimal(
                        step.importance
                    )
                ),
                "progress_status": (
                    step.progress_status
                ),
            }
        )

    return {
        "career_id": (
            overview.career_id
        ),
        "career_name": (
            overview.career_name
        ),
        "score_status": (
            _value(
                overview.score_status
            )
        ),
        "readiness_score": (
            _decimal(
                overview.readiness_score
            )
        ),
        "roadmap_steps": (
            steps
        ),
    }


def build_roadmap_guidance_cache_key(
    *,
    profile_context,
    roadmap_source: Mapping[
        str,
        object,
    ],
    model: str,
) -> str:
    """
    Fingerprint approved profile context plus relevant roadmap state.

    Raw Student Profile data is not stored in the snapshot.
    """

    source = {
        "version": (
            ROADMAP_GUIDANCE_VERSION
        ),
        "model": model,
        "profile": (
            profile_context.model_dump(
                mode="json"
            )
        ),
        "roadmap": dict(
            roadmap_source
        ),
    }

    serialized = json.dumps(
        source,
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


def align_guidance_items(
    *,
    guidance_items,
    roadmap_steps,
):
    """
    Enforce the deterministic roadmap Skill set and order.

    AI wording is accepted only when every supplied Skill
    appears exactly once.
    """

    expected_steps = list(
        roadmap_steps
    )

    if (
        len(
            guidance_items
        )
        != len(
            expected_steps
        )
    ):
        raise AIResponseValidationError(
            "Roadmap AI guidance count does not "
            "match deterministic roadmap step count."
        )

    by_skill = {}

    for item in guidance_items:

        key = (
            item.skill_name
            .strip()
            .casefold()
        )

        if key in by_skill:
            raise AIResponseValidationError(
                "Roadmap AI guidance contains a "
                "duplicate Skill."
            )

        by_skill[
            key
        ] = item

    aligned = []

    for step in expected_steps:

        skill_name = str(
            step.get(
                "skill_name",
                "",
            )
        ).strip()

        key = (
            skill_name.casefold()
        )

        if (
            not skill_name
            or key not in by_skill
        ):
            raise AIResponseValidationError(
                "Roadmap AI guidance does not match "
                f"deterministic Skill: {skill_name}."
            )

        item = by_skill[
            key
        ]

        aligned.append(
            {
                "skill_name": (
                    skill_name
                ),
                "why_this_matters": (
                    item
                    .why_this_matters
                    .strip()
                ),
                "your_focus": (
                    item
                    .your_focus
                    .strip()
                ),
            }
        )

    return aligned


def generate_roadmap_guidance(
    *,
    profile_context,
    roadmap_source,
    provider,
):
    """
    Generate validated AI wording only.

    The deterministic roadmap itself is never modified.
    """

    roadmap_steps = list(
        roadmap_source.get(
            "roadmap_steps",
            []
        )
    )

    if not roadmap_steps:
        return []

    prompt_package = (
        build_roadmap_guidance_prompt(
            profile=profile_context,
            roadmap_context=(
                roadmap_source
            ),
        )
    )

    result = provider.generate(
        prompt_package=(
            prompt_package
        ),
        output_model=(
            RoadmapGuidanceExplanation
        ),
    )

    return align_guidance_items(
        guidance_items=(
            result.guidance_items
        ),
        roadmap_steps=(
            roadmap_steps
        ),
    )


def build_fallback_roadmap_guidance(
    roadmap_source,
):
    """
    Grounded deterministic fallback.

    This keeps the Career Roadmap usable when AI is unavailable.
    """

    career_name = str(
        roadmap_source.get(
            "career_name",
            "",
        )
    ).strip()

    results = []

    for step in (
        roadmap_source.get(
            "roadmap_steps",
            []
        )
    ):
        skill_name = str(
            step.get(
                "skill_name",
                "",
            )
        ).strip()

        current_proficiency = (
            step.get(
                "current_proficiency"
            )
        )

        why = (
            f"{skill_name} is one of your current "
            f"priority skill gaps"
        )

        if career_name:
            why += (
                f" for {career_name}"
            )

        why += "."

        if current_proficiency:
            focus = (
                f"Build stronger evidence in {skill_name} "
                "and work toward the required level."
            )
        else:
            focus = (
                f"Start building evidence in {skill_name} "
                "through a relevant learning activity or project."
            )

        results.append(
            {
                "skill_name": (
                    skill_name
                ),
                "why_this_matters": (
                    why
                ),
                "your_focus": (
                    focus
                ),
            }
        )

    return results


def get_cached_roadmap_guidance(
    *,
    student_profile_id: int,
    career_id: int,
    cache_key: str,
    model: str,
):
    return (
        RoadmapGuidanceSnapshot
        .objects
        .filter(
            student_profile_id=(
                student_profile_id
            ),
            career_id=career_id,
            cache_key=cache_key,
            guidance_version=(
                ROADMAP_GUIDANCE_VERSION
            ),
            model=model,
        )
        .first()
    )


def store_roadmap_guidance(
    *,
    student_profile_id: int,
    career_id: int,
    cache_key: str,
    model: str,
    payload,
    prompt_tokens: int = 0,
    total_tokens: int = 0,
):
    snapshot, _ = (
        RoadmapGuidanceSnapshot
        .objects
        .update_or_create(
            student_profile_id=(
                student_profile_id
            ),
            career_id=career_id,
            defaults={
                "cache_key": (
                    cache_key
                ),
                "guidance_version": (
                    ROADMAP_GUIDANCE_VERSION
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


def get_or_generate_roadmap_guidance(
    *,
    student_profile,
    overview,
    provider,
    model: str,
):
    """
    Cache-first Roadmap AI orchestration.

    Result keys:

    career_id
    career_name
    guidance_items
    is_ai_generated
    fallback
    model
    version
    usage
    cached
    """

    profile_context = (
        build_student_profile_context(
            student_profile=(
                student_profile
            )
        )
    )

    roadmap_source = (
        build_roadmap_guidance_source(
            overview
        )
    )

    if not roadmap_source[
        "roadmap_steps"
    ]:
        return {
            "career_id": (
                overview.career_id
            ),
            "career_name": (
                overview.career_name
            ),
            "guidance_items": [],
            "is_ai_generated": False,
            "fallback": False,
            "model": model,
            "version": (
                ROADMAP_GUIDANCE_VERSION
            ),
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            },
            "cached": False,
        }

    cache_key = (
        build_roadmap_guidance_cache_key(
            profile_context=(
                profile_context
            ),
            roadmap_source=(
                roadmap_source
            ),
            model=model,
        )
    )

    cached = (
        get_cached_roadmap_guidance(
            student_profile_id=(
                student_profile.id
            ),
            career_id=(
                overview.career_id
            ),
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
            generate_roadmap_guidance(
                profile_context=(
                    profile_context
                ),
                roadmap_source=(
                    roadmap_source
                ),
                provider=provider,
            )
        )

    except AIProviderError:
        return {
            "career_id": (
                overview.career_id
            ),
            "career_name": (
                overview.career_name
            ),
            "guidance_items": (
                build_fallback_roadmap_guidance(
                    roadmap_source
                )
            ),
            "is_ai_generated": False,
            "fallback": True,
            "model": model,
            "version": (
                ROADMAP_GUIDANCE_VERSION
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
            overview.career_id
        ),
        "career_name": (
            overview.career_name
        ),
        "guidance_items": (
            guidance_items
        ),
        "is_ai_generated": True,
        "fallback": False,
        "model": model,
        "version": (
            ROADMAP_GUIDANCE_VERSION
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

    store_roadmap_guidance(
        student_profile_id=(
            student_profile.id
        ),
        career_id=(
            overview.career_id
        ),
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
