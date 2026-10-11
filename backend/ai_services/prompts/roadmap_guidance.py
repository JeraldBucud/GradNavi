"""
Personalised Career Roadmap guidance prompt.

The Career Roadmap is already calculated before AI runs.

AI only explains the supplied deterministic roadmap steps
using approved Student Profile context.
"""

import json

from ai_services.prompts.common import (
    AIOperation,
    PromptPackage,
)
from ai_services.safety.policies import (
    get_common_safety_rules,
)


SYSTEM_INSTRUCTIONS: tuple[str, ...] = (
    (
        "Explain the supplied Career Roadmap steps directly "
        "to the Student."
    ),
    (
        "Use only the supplied deterministic roadmap data and "
        "approved Student Profile context."
    ),
    (
        "Address the Student using 'you' and 'your'."
    ),
    (
        "Personalise guidance only when the supplied profile "
        "contains relevant evidence."
    ),
    (
        "The supplied roadmap_steps are selected and ordered "
        "deterministically by GradNavi."
    ),
    (
        "Never change, replace, reorder, add, or remove "
        "roadmap Skills."
    ),
    (
        "Never calculate or alter Readiness Scores, Skill Gap "
        "values, requirement levels, importance values, "
        "progress states, or priorities."
    ),
    (
        "Do not invent Student experience, projects, skills, "
        "education, qualifications, achievements, or evidence."
    ),
    (
        "Do not treat a Career Goal as completed experience."
    ),
    (
        "Do not claim guaranteed employment, suitability, "
        "career success, or hiring outcomes."
    ),
    (
        "Use concise Student-facing language."
    ),
)


OUTPUT_REQUIREMENTS: tuple[str, ...] = (
    (
        "Return content matching the GradNavi "
        "RoadmapGuidanceExplanation structure."
    ),
    (
        "Return exactly one guidance item for every supplied "
        "roadmap step."
    ),
    (
        "Use the exact supplied skill_name for every item."
    ),
    (
        "Preserve the supplied roadmap order."
    ),
    (
        "why_this_matters should explain why the Skill is "
        "relevant to the Student's current roadmap."
    ),
    (
        "your_focus should give one concise grounded focus "
        "for the Student."
    ),
    (
        "Do not use Markdown headings or tables."
    ),
    (
        "Set is_ai_generated to true."
    ),
)


def _trusted_profile_context(
    profile,
) -> dict:
    """
    Keep structural Student Profile facts in trusted context.

    Student-written descriptions stay outside this section.
    """

    return {
        "skills": [
            {
                "name": item.name,
                "proficiency_level": (
                    item.proficiency_level
                ),
            }
            for item in profile.skills
        ],
        "education": [
            {
                "institution_name": (
                    item.institution_name
                ),
                "qualification": (
                    item.qualification
                ),
                "field_of_study": (
                    item.field_of_study
                ),
                "start_date": (
                    item.start_date.isoformat()
                ),
                "end_date": (
                    item.end_date.isoformat()
                    if item.end_date
                    is not None
                    else None
                ),
            }
            for item in profile.education
        ],
        "experience": [
            {
                "job_title": (
                    item.job_title
                ),
                "company": item.company,
                "start_date": (
                    item.start_date.isoformat()
                ),
                "end_date": (
                    item.end_date.isoformat()
                    if item.end_date
                    is not None
                    else None
                ),
                "is_current": (
                    item.is_current
                ),
            }
            for item in profile.experience
        ],
        "projects": [
            {
                "name": item.name,
                "start_date": (
                    item.start_date.isoformat()
                ),
                "end_date": (
                    item.end_date.isoformat()
                    if item.end_date
                    is not None
                    else None
                ),
            }
            for item in profile.projects
        ],
        "career_goals": [
            {
                "target_role": (
                    item.target_role
                ),
            }
            for item in profile.career_goals
        ],
    }


def _untrusted_profile_content(
    profile,
) -> str:
    """
    Student-authored descriptions stay explicitly untrusted.
    """

    content = {
        "education_descriptions": [
            {
                "institution_name": (
                    item.institution_name
                ),
                "description": (
                    item.description
                ),
            }
            for item in profile.education
            if item.description
        ],
        "experience_descriptions": [
            {
                "job_title": (
                    item.job_title
                ),
                "company": (
                    item.company
                ),
                "description": (
                    item.description
                ),
            }
            for item in profile.experience
            if item.description
        ],
        "project_descriptions": [
            {
                "project_name": (
                    item.name
                ),
                "description": (
                    item.description
                ),
            }
            for item in profile.projects
            if item.description
        ],
        "career_goal_descriptions": [
            {
                "target_role": (
                    item.target_role
                ),
                "description": (
                    item.description
                ),
            }
            for item in profile.career_goals
            if item.description
        ],
    }

    rendered = json.dumps(
        content,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )

    return (
        "<UNTRUSTED_PROFILE_DESCRIPTIONS>\n"
        f"{rendered}\n"
        "</UNTRUSTED_PROFILE_DESCRIPTIONS>"
    )


def build_roadmap_guidance_prompt(
    *,
    profile,
    roadmap_context,
) -> PromptPackage:

    trusted_context = {
        "student_profile": (
            _trusted_profile_context(
                profile
            )
        ),
        "career_roadmap": dict(
            roadmap_context
        ),
    }

    return PromptPackage(
        operation=(
            AIOperation
            .ROADMAP_GUIDANCE
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
            _untrusted_profile_content(
                profile
            )
        ),
        output_requirements=(
            OUTPUT_REQUIREMENTS
        ),
    )
