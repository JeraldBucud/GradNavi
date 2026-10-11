"""
AI Gap Summary prompt for GradNavi.

All readiness scores, requirement statuses, gap ordering,
and learning-resource matches are deterministic before AI runs.

AI only explains those supplied results and proposes
grounded next actions.
"""

import json
from collections.abc import Mapping

from ai_services.prompts.common import (
    AIOperation,
    PromptPackage,
)
from ai_services.safety.policies import (
    get_common_safety_rules,
)


SYSTEM_INSTRUCTIONS: tuple[str, ...] = (
    (
        "Explain the supplied Skill Gap Analysis directly to the Student "
        "using only the deterministic GradNavi results supplied."
    ),
    (
        "Address the Student using 'you' and 'your'."
    ),
    (
        "Explain the main reasons the current Readiness Score is at its "
        "current level."
    ),
    (
        "Use the supplied highest-priority gaps and any supplied strengths "
        "when explaining readiness."
    ),
    (
        "The supplied fix_first list is selected deterministically by "
        "GradNavi. Never change, replace, reorder, or skip those items."
    ),
    (
        "Write one recommended next step for each fix_first item, preserving "
        "the exact fix_first order."
    ),
    (
        "Do not describe a gap as largest, second-highest, most important, "
        "or similar unless that description is explicitly supplied."
    ),
    (
        "Do not say a gap contributes most, drives the score most, has the "
        "largest effect, or similar unless that fact is explicitly supplied."
    ),
    (
        "Recommend practical next actions that address only the supplied "
        "gaps."
    ),
    (
        "Do not calculate, change, reinterpret, or override the Readiness "
        "Score, requirement statuses, gap amounts, priorities, or counts."
    ),
    (
        "Do not invent Student skills, qualifications, projects, experience, "
        "evidence, requirements, or Learning Resources."
    ),
    (
        "Do not name a Learning Resource unless it appears in the supplied "
        "controlled resource list."
    ),
    (
        "If no Learning Resources are supplied, do not invent courses, "
        "providers, links, tutorials, or resources."
    ),
    (
        "Do not claim guaranteed career success, employment, suitability, "
        "or hiring outcomes."
    ),
    (
        "Use concise, natural Student-facing language."
    ),
)


OUTPUT_REQUIREMENTS: tuple[str, ...] = (
    (
        "Return content matching the GradNavi SkillGapSummaryExplanation "
        "structured output."
    ),
    (
        "readiness_explanation should use 2 or 3 concise sentences."
    ),
    (
        "Explain why readiness is at its current level without restating "
        "every requirement."
    ),
    (
        "recommended_next_steps must contain exactly one concise action for "
        "each supplied fix_first item. There may be 1, 2, or 3 actions."
    ),
    (
        "The actions must correspond one-to-one with the supplied fix_first "
        "items and preserve their deterministic order."
    ),
    (
        "Each next step must name or clearly refer to its corresponding "
        "fix_first skill."
    ),
    (
        "Do not use Markdown headings or tables."
    ),
    (
        "Set is_ai_generated to true."
    ),
)


def build_skill_gap_summary_prompt(
    context: Mapping[str, object],
) -> PromptPackage:
    return PromptPackage(
        operation=(
            AIOperation
            .SKILL_GAP_SUMMARY
        ),
        system_instructions=(
            SYSTEM_INSTRUCTIONS
        ),
        safety_rules=(
            get_common_safety_rules()
        ),
        trusted_context=(
            json.dumps(
                dict(context),
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )
        ),
        untrusted_content=(
            "None. This operation uses only "
            "GradNavi-controlled deterministic results."
        ),
        output_requirements=(
            OUTPUT_REQUIREMENTS
        ),
    )
