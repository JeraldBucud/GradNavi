"""
Learning Resource discovery prompt contract.

This prompt prepares trusted GradNavi Skill context for
a provider that supports current web discovery.

The provider must return real external resource URLs.
"""

import json

from ai_services.prompts.common import (
    AIOperation,
    PromptPackage,
)
from ai_services.safety.policies import (
    get_common_safety_rules,
)
from ai_services.schemas.inputs import (
    LearningResourceDiscoveryInput,
)


SYSTEM_INSTRUCTIONS: tuple[str, ...] = (
    (
        "Find real third-party learning resources for the "
        "supplied canonical GradNavi Skill."
    ),
    (
        "Use current web-search evidence before returning "
        "a resource."
    ),
    (
        "Never invent or guess a resource URL, provider, "
        "title, price model, or resource type."
    ),
    (
        "Return direct learning-resource pages when available, "
        "not search-result pages."
    ),
    (
        "Prefer official documentation, recognised education "
        "providers, established universities, and reputable "
        "learning platforms."
    ),
    (
        "Do not return a URL already listed in existing_urls."
    ),
    (
        "The Skill is the primary relevance requirement. "
        "Career context is supporting context only."
    ),
    (
        "Do not use Student Profile information. Discovery "
        "does not require personal Student data."
    ),
    (
        "If access_type is free, freemium, or paid, return only "
        "resources whose access model supports that filter."
    ),
    (
        "If the access model cannot be confirmed and the filter "
        "is all, classify the resource as unknown."
    ),
    (
        "Return fewer resources, including zero, when suitable "
        "real resources cannot be verified."
    ),
)


OUTPUT_REQUIREMENTS: tuple[str, ...] = (
    (
        "Return content matching the GradNavi "
        "LearningResourceDiscoveryResult structure."
    ),
    (
        "Return no more candidates than requested_count."
    ),
    (
        "Every candidate must contain title, provider, URL, "
        "resource_type, access_type, and description."
    ),
    (
        "Keep candidate descriptions concise plain text. "
        "Do not include Markdown links, citations, source "
        "annotations, or URLs inside description."
    ),
    (
        "Classify access_type from the web evidence as free, "
        "freemium, or paid whenever the evidence supports one "
        "of those values. Use unknown only when the available "
        "source evidence does not establish the access model. "
        "Do not use unknown merely because registration or an "
        "account may be required."
    ),
    (
        "Every URL must use HTTP or HTTPS."
    ),
    (
        "Candidate URLs must be unique."
    ),
    (
        "resource_type must be course, documentation, article, "
        "video, tutorial, book, or other."
    ),
    (
        "access_type must be free, freemium, paid, or unknown."
    ),
    (
        "Set is_ai_generated to true."
    ),
)


def build_learning_resource_discovery_prompt(
    request: LearningResourceDiscoveryInput,
) -> PromptPackage:
    trusted_context = {
        "skill_name": (
            request.skill_name
        ),
        "skill_description": (
            request.skill_description
        ),
        "career_name": (
            request.career_name
        ),
        "access_type": (
            request.access_type
        ),
        "requested_count": (
            request.requested_count
        ),
        "existing_urls": (
            request.existing_urls
        ),
    }

    return PromptPackage(
        operation=(
            AIOperation
            .LEARNING_RESOURCE_DISCOVERY
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
            )
        ),
        untrusted_content="",
        output_requirements=(
            OUTPUT_REQUIREMENTS
        ),
    )
