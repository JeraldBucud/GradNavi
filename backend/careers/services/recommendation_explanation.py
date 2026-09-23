"""
Top Career Recommendation explanation service.

Career recommendation calculation remains deterministic.

This service only explains existing recommendation evidence.
"""

from collections.abc import (
    Mapping,
)

from ai_services.exceptions import (
    AIInputError,
)
from ai_services.prompts.career_match_explanation import (
    build_career_match_explanation_prompt,
)
from ai_services.providers.base import (
    AIProvider,
)
from ai_services.schemas.outputs import (
    CareerMatchExplanation,
)


EXPLANATION_VERSION = (
    "career_match_explanation_v2"
)


def select_top_recommendation(
    payload: Mapping[str, object],
) -> dict:
    recommendations = (
        payload.get(
            "recommendations"
        )
    )

    if (
        not isinstance(
            recommendations,
            list,
        )
        or not recommendations
    ):
        raise AIInputError(
            "Recommendation snapshot contains no recommendations."
        )

    valid = [
        item
        for item
        in recommendations
        if isinstance(
            item,
            dict,
        )
    ]

    if not valid:
        raise AIInputError(
            "Recommendation snapshot contains no valid recommendations."
        )

    def rank_key(
        item,
    ):
        rank = (
            item.get(
                "rank"
            )
        )

        if isinstance(
            rank,
            int,
        ):
            return rank

        return 999999

    return min(
        valid,
        key=rank_key,
    )


def generate_top_match_explanation(
    *,
    recommendation: Mapping[str, object],
    provider: AIProvider,
) -> CareerMatchExplanation:
    prompt_package = (
        build_career_match_explanation_prompt(
            recommendation
        )
    )

    return provider.generate(
        prompt_package=(
            prompt_package
        ),
        output_model=(
            CareerMatchExplanation
        ),
    )
