"""
Personalised Learning Resource guidance prompt.

Resource selection and ranking are deterministic before AI runs.

AI writes only the Student-facing Why This Fits You explanation.
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
        "Explain why each supplied Learning Resource fits "
        "the Student's current Skill gap."
    ),
    (
        "Use only the supplied deterministic resource "
        "recommendations and approved Student Profile context."
    ),
    (
        "Address the Student using 'you' and 'your'."
    ),
    (
        "Personalise wording only when relevant supporting "
        "Student evidence is supplied."
    ),
    (
        "The supplied resources have already been selected "
        "and ranked by GradNavi."
    ),
    (
        "Never add, remove, replace, rank, reorder, or score "
        "Learning Resources."
    ),
    (
        "Never change Skill Gap values, Career Readiness "
        "values, roadmap priority, or recommendation scores."
    ),
    (
        "Do not invent Student skills, qualifications, "
        "experience, education, projects, achievements, "
        "or evidence."
    ),
    (
        "Do not invent resource outcomes, accreditation, "
        "quality ratings, completion times, prices, or "
        "features that were not supplied."
    ),
    (
        "Do not claim a resource guarantees employment, "
        "career success, certification, or Skill mastery."
    ),
    (
        "Use concise Student-facing language."
    ),
)


OUTPUT_REQUIREMENTS: tuple[str, ...] = (
    (
        "Return content matching the GradNavi "
        "LearningResourceGuidanceExplanation structure."
    ),
    (
        "Return exactly one guidance item for every supplied "
        "resource."
    ),
    (
        "Use the exact supplied resource_id."
    ),
    (
        "Preserve the supplied resource order."
    ),
    (
        "why_this_fits should explain the connection between "
        "the Student, Skill gap, selected Career, and resource."
    ),
    (
        "Keep each explanation concise."
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
                "company": (
                    item.company
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


def _untrusted_content(
    *,
    profile,
    resource_context,
) -> str:

    content = {
        "student_profile_descriptions": {
            "education": [
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
            "experience": [
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
            "projects": [
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
            "career_goals": [
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
        },
        "resource_descriptions": [
            {
                "resource_id": (
                    resource.get(
                        "resource_id"
                    )
                ),
                "description": (
                    resource.get(
                        "description",
                        "",
                    )
                ),
            }
            for resource
            in resource_context.get(
                "resources",
                []
            )
            if resource.get(
                "description"
            )
        ],
    }

    rendered = json.dumps(
        content,
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )

    return (
        "<UNTRUSTED_CONTEXT>\n"
        f"{rendered}\n"
        "</UNTRUSTED_CONTEXT>"
    )


def build_learning_resource_guidance_prompt(
    *,
    profile,
    resource_context,
) -> PromptPackage:

    safe_resources = [
        {
            "resource_id": (
                item.get(
                    "resource_id"
                )
            ),
            "title": (
                item.get(
                    "title"
                )
            ),
            "provider": (
                item.get(
                    "provider"
                )
            ),
            "resource_type": (
                item.get(
                    "resource_type"
                )
            ),
            "access_type": (
                item.get(
                    "access_type"
                )
            ),
            "feedback_score": (
                item.get(
                    "feedback_score"
                )
            ),
            "fallback_explanation": (
                item.get(
                    "fallback_explanation"
                )
            ),
        }
        for item
        in resource_context.get(
            "resources",
            []
        )
    ]

    trusted_context = {
        "student_profile": (
            _trusted_profile_context(
                profile
            )
        ),
        "career_id": (
            resource_context.get(
                "career_id"
            )
        ),
        "career_name": (
            resource_context.get(
                "career_name"
            )
        ),
        "skill_id": (
            resource_context.get(
                "skill_id"
            )
        ),
        "skill_name": (
            resource_context.get(
                "skill_name"
            )
        ),
        "resources": (
            safe_resources
        ),
    }

    return PromptPackage(
        operation=(
            AIOperation
            .LEARNING_RESOURCE_GUIDANCE
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
            _untrusted_content(
                profile=profile,
                resource_context=(
                    resource_context
                ),
            )
        ),
        output_requirements=(
            OUTPUT_REQUIREMENTS
        ),
    )
