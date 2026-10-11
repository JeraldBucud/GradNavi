"""
Career Match explanation prompt for GradNavi.

The Career Recommendation is already calculated before this AI operation.

AI only explains the supplied deterministic evidence.
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
        "Explain the Career Recommendation directly to the Student using "
        "only the deterministic GradNavi evidence supplied."
    ),
    (
        "Address the Student using 'you' and 'your'."
    ),
    (
        "Start with the strongest supplied evidence for the career, such as "
        "competencies or technologies."
    ),
    (
        "If a priority gap is supplied, mention at most one development "
        "area in the final sentence."
    ),
    (
        "Do not repeat the Career Match score or rank unless it is necessary "
        "to make the explanation understandable."
    ),
    (
        "Do not use internal GradNavi terminology such as 'matched "
        "competencies', 'recommendation evidence', 'career match shows', "
        "'supplied evidence', or 'the student'."
    ),
    (
        "Do not invent skills, technologies, qualifications, experience, "
        "education, projects, interests, achievements, or career evidence."
    ),
    (
        "Do not change, recalculate, reinterpret, or override the Career "
        "Match score, rank, Readiness score, or Skill Gap calculations."
    ),
    (
        "Do not claim guaranteed career success, employment, suitability, "
        "or hiring outcomes."
    ),
    (
        "Use natural, concise Student-facing language."
    ),
)


OUTPUT_REQUIREMENTS: tuple[str, ...] = (
    (
        "Return content matching the GradNavi CareerMatchExplanation "
        "structured output."
    ),
    (
        "Write exactly 2 concise sentences."
    ),
    (
        "Sentence 1 should explain the strongest evidence supporting "
        "the career match."
    ),
    (
        "Sentence 2 should identify the main development area when one "
        "is supplied; otherwise reinforce the strongest evidence."
    ),
    (
        "Keep the explanation under 320 characters where practical."
    ),
    (
        "Do not use Markdown, headings, bullet points, or tables."
    ),
    (
        "Set is_ai_generated to true."
    ),
)


def _clean_items(
    value,
    *,
    limit: int,
) -> list[str]:
    if not isinstance(
        value,
        (list, tuple),
    ):
        return []

    cleaned = []

    seen = set()

    for item in value:
        if not isinstance(
            item,
            str,
        ):
            continue

        normalized = (
            item.strip()
        )

        if not normalized:
            continue

        key = (
            normalized.casefold()
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        cleaned.append(
            normalized
        )

        if len(cleaned) >= limit:
            break

    return cleaned


def build_career_match_explanation_prompt(
    recommendation: Mapping[str, object],
) -> PromptPackage:
    """
    Build a minimal prompt using only existing recommendation evidence.

    Raw Student Profile data is deliberately excluded.
    """

    career_name = str(
        recommendation.get(
            "career_name",
            "",
        )
    ).strip()

    if not career_name:
        raise ValueError(
            "career_name is required."
        )

    trusted_context = {
        "career_name": (
            career_name
        ),
        "career_match_score": (
            recommendation.get(
                "recommendation_score"
            )
        ),
        "rank": (
            recommendation.get(
                "rank"
            )
        ),
        "matched_competencies": (
            _clean_items(
                recommendation.get(
                    "matched_competencies"
                ),
                limit=3,
            )
        ),
        "matched_technologies": (
            _clean_items(
                recommendation.get(
                    "matched_technologies"
                ),
                limit=2,
            )
        ),
        "priority_gaps": (
            _clean_items(
                recommendation.get(
                    "missing_competencies"
                ),
                limit=1,
            )
        ),
    }

    return PromptPackage(
        operation=(
            AIOperation
            .CAREER_MATCH_EXPLANATION
        ),
        system_instructions=(
            SYSTEM_INSTRUCTIONS
        ),
        safety_rules=(
            get_common_safety_rules()
        ),
        trusted_context=(
            json.dumps(
                trusted_context,
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )
        ),
        untrusted_content=(
            "None. This operation uses only "
            "GradNavi-controlled recommendation evidence."
        ),
        output_requirements=(
            OUTPUT_REQUIREMENTS
        ),
    )
