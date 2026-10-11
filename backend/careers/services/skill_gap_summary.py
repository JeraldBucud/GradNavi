"""
AI Gap Summary orchestration and persistent cache support.

The deterministic WBS 5.5 readiness result remains authoritative.
"""

import hashlib
import json
from collections.abc import Mapping

from ai_services.exceptions import (
    AIResponseValidationError,
)
from ai_services.prompts.skill_gap_summary import (
    build_skill_gap_summary_prompt,
)
from ai_services.providers.base import (
    AIProvider,
)
from ai_services.schemas.outputs import (
    SkillGapSummaryExplanation,
)
from careers.models import (
    SkillGapSummarySnapshot,
)
from careers.services.readiness_scoring import (
    GapStatus,
)


SKILL_GAP_SUMMARY_VERSION = (
    "skill_gap_summary_v3"
)

MAX_PROMPT_GAPS = 6

MAX_PROMPT_STRENGTHS = 3

MAX_FIX_FIRST = 3

MAX_RESOURCE_TITLES = 3


def _enum_value(
    value,
):
    return getattr(
        value,
        "value",
        value,
    )


def _decimal_value(
    value,
):
    if value is None:
        return None

    return str(
        value
    )


def build_skill_gap_summary_source(
    plan,
) -> dict:
    """
    Build the full deterministic source used for cache invalidation.

    All requirements are included in the fingerprint even though
    only a smaller subset is sent to the text-generation model.
    """

    readiness = (
        plan.readiness_result
    )

    requirements = []

    for gap in readiness.skill_gaps:
        requirements.append(
            {
                "skill_id": (
                    gap.skill_id
                ),
                "skill_name": (
                    gap.skill_name
                ),
                "status": (
                    _enum_value(
                        gap.gap_status
                    )
                ),
                "current_proficiency": (
                    gap.student_proficiency_level
                ),
                "current_score": (
                    _decimal_value(
                        gap.student_proficiency_score
                    )
                ),
                "required_level": (
                    _decimal_value(
                        gap.required_level
                    )
                ),
                "gap_amount": (
                    _decimal_value(
                        gap.gap_amount
                    )
                ),
                "importance": (
                    _decimal_value(
                        gap.importance
                    )
                ),
            }
        )

    resources = []

    seen_resource_ids = set()

    for suggestion in plan.suggestions:
        for resource in (
            suggestion.resources
            or ()
        ):
            if resource.id in seen_resource_ids:
                continue

            seen_resource_ids.add(
                resource.id
            )

            resources.append(
                {
                    "id": resource.id,
                    "title": resource.title,
                    "provider": resource.provider,
                    "resource_type": (
                        resource.resource_type
                    ),
                    "url": resource.url,
                }
            )

    return {
        "career_id": (
            readiness.career_id
        ),
        "career_name": (
            readiness.career_name
        ),
        "score_status": (
            _enum_value(
                readiness.score_status
            )
        ),
        "readiness_score": (
            _decimal_value(
                readiness.readiness_score
            )
        ),
        "meets_requirement_count": (
            readiness.meets_requirement_count
        ),
        "below_requirement_count": (
            readiness.below_requirement_count
        ),
        "missing_requirement_count": (
            readiness.missing_requirement_count
        ),
        "requirements": (
            requirements
        ),
        "learning_resources": (
            resources
        ),
    }


def build_skill_gap_summary_cache_key(
    source: Mapping[str, object],
    *,
    model: str,
) -> str:
    fingerprint_source = {
        "summary_version": (
            SKILL_GAP_SUMMARY_VERSION
        ),
        "model": model,
        "source": dict(
            source
        ),
    }

    serialized = json.dumps(
        fingerprint_source,
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


def build_fix_first(
    plan,
) -> list[dict]:
    unresolved = [
        gap
        for gap
        in plan.readiness_result.skill_gaps
        if gap.gap_status
        != GapStatus.MEETS_REQUIREMENT
    ]

    return [
        {
            "skill_id": (
                gap.skill_id
            ),
            "skill_name": (
                gap.skill_name
            ),
            "status": (
                _enum_value(
                    gap.gap_status
                )
            ),
        }
        for gap
        in unresolved[
            :MAX_FIX_FIRST
        ]
    ]


def build_skill_gap_prompt_context(
    source: Mapping[str, object],
) -> dict:
    requirements = list(
        source.get(
            "requirements",
            []
        )
    )

    unresolved = [
        item
        for item
        in requirements
        if item.get(
            "status"
        )
        != GapStatus.MEETS_REQUIREMENT.value
    ]

    strengths = [
        item
        for item
        in requirements
        if item.get(
            "status"
        )
        == GapStatus.MEETS_REQUIREMENT.value
    ]

    resource_titles = [
        item.get(
            "title"
        )
        for item
        in source.get(
            "learning_resources",
            []
        )
        if item.get(
            "title"
        )
    ]

    return {
        "career_name": (
            source.get(
                "career_name"
            )
        ),
        "readiness_score": (
            source.get(
                "readiness_score"
            )
        ),
        "meets_requirement_count": (
            source.get(
                "meets_requirement_count"
            )
        ),
        "below_requirement_count": (
            source.get(
                "below_requirement_count"
            )
        ),
        "missing_requirement_count": (
            source.get(
                "missing_requirement_count"
            )
        ),
        "fix_first": (
            unresolved[
                :MAX_FIX_FIRST
            ]
        ),
        "highest_priority_gaps": (
            unresolved[
                :MAX_PROMPT_GAPS
            ]
        ),
        "existing_strengths": (
            strengths[
                :MAX_PROMPT_STRENGTHS
            ]
        ),
        "available_learning_resources": (
            resource_titles[
                :MAX_RESOURCE_TITLES
            ]
        ),
    }


def align_next_steps_to_fix_first(
    *,
    recommended_next_steps,
    fix_first,
) -> list[str]:
    """
    Align AI-written action wording to the authoritative
    deterministic WBS 5.5 Fix First order.

    AI may write the wording.

    AI may not choose or reorder the Skill priorities.
    """

    cleaned_steps = [
        step.strip()
        for step
        in recommended_next_steps
        if isinstance(
            step,
            str,
        )
        and step.strip()
    ]

    if len(cleaned_steps) != len(
        fix_first
    ):
        raise AIResponseValidationError(
            "AI Gap Summary action count does not "
            "match deterministic Fix First count."
        )

    aligned = []

    used_indexes = set()

    for item in fix_first:

        skill_name = str(
            item.get(
                "skill_name",
                "",
            )
        ).strip()

        if not skill_name:
            raise AIResponseValidationError(
                "Deterministic Fix First item "
                "has no skill name."
            )

        matching_indexes = [
            index
            for index, step
            in enumerate(
                cleaned_steps
            )
            if (
                index
                not in used_indexes
                and skill_name.casefold()
                in step.casefold()
            )
        ]

        if len(
            matching_indexes
        ) != 1:
            raise AIResponseValidationError(
                "AI Gap Summary must contain exactly "
                "one action for deterministic Fix First "
                f"skill: {skill_name}."
            )

        match_index = (
            matching_indexes[0]
        )

        used_indexes.add(
            match_index
        )

        aligned.append(
            cleaned_steps[
                match_index
            ]
        )

    if len(
        used_indexes
    ) != len(
        cleaned_steps
    ):
        raise AIResponseValidationError(
            "AI Gap Summary returned an action that "
            "does not map to deterministic Fix First."
        )

    return aligned


def generate_skill_gap_summary(
    *,
    source: Mapping[str, object],
    provider: AIProvider,
) -> SkillGapSummaryExplanation:
    prompt_context = (
        build_skill_gap_prompt_context(
            source
        )
    )

    prompt_package = (
        build_skill_gap_summary_prompt(
            prompt_context
        )
    )

    result = provider.generate(
        prompt_package=(
            prompt_package
        ),
        output_model=(
            SkillGapSummaryExplanation
        ),
    )

    aligned_steps = (
        align_next_steps_to_fix_first(
            recommended_next_steps=(
                result
                .recommended_next_steps
            ),
            fix_first=(
                prompt_context[
                    "fix_first"
                ]
            ),
        )
    )

    return (
        SkillGapSummaryExplanation(
            readiness_explanation=(
                result
                .readiness_explanation
                .strip()
            ),
            recommended_next_steps=(
                aligned_steps
            ),
            is_ai_generated=True,
        )
    )


def get_cached_skill_gap_summary(
    *,
    student_profile_id: int,
    career_id: int,
    cache_key: str,
    model: str,
):
    return (
        SkillGapSummarySnapshot
        .objects
        .filter(
            student_profile_id=(
                student_profile_id
            ),
            career_id=career_id,
            cache_key=cache_key,
            summary_version=(
                SKILL_GAP_SUMMARY_VERSION
            ),
            model=model,
        )
        .first()
    )


def store_skill_gap_summary(
    *,
    student_profile_id: int,
    career_id: int,
    cache_key: str,
    model: str,
    payload: Mapping[str, object],
):
    snapshot, _ = (
        SkillGapSummarySnapshot
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
                "summary_version": (
                    SKILL_GAP_SUMMARY_VERSION
                ),
                "model": model,
                "payload": dict(
                    payload
                ),
            },
        )
    )

    return snapshot
