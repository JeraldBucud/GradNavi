"""
Learning suggestions and roadmap generation for GradNavi.

WBS 5.7 consumes WBS 5.5 readiness output. It does not calculate
skill gaps, readiness scores, or roadmap priority independently.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from careers.models import LearningResource
from careers.services import readiness_scoring
from careers.services.readiness_scoring import (
    CareerReadinessResult,
    GapStatus,
    SkillGapResult,
)


UNRESOLVED_GAP_STATUSES = (
    GapStatus.MISSING,
    GapStatus.BELOW_REQUIREMENT,
)


@dataclass(frozen=True)
class LearningResourceSummary:
    """
    Structured learning-resource data ready for API serialization.
    """

    id: int
    title: str
    provider: str
    url: str
    resource_type: str
    description: str


@dataclass(frozen=True)
class LearningSuggestion:
    """
    Learning resources associated with one unresolved WBS 5.5 gap.
    """

    priority: int
    skill_id: int
    skill_name: str
    gap_status: GapStatus
    current_proficiency: str | None
    current_score: Decimal
    required_level: Decimal
    gap_amount: Decimal
    importance: Decimal
    resources: tuple[LearningResourceSummary, ...]


@dataclass(frozen=True)
class RoadmapStep:
    """
    Ordered development step derived from one unresolved WBS 5.5 gap.
    """

    step_number: int
    skill_id: int
    skill_name: str
    gap_status: GapStatus
    current_proficiency: str | None
    current_score: Decimal
    required_level: Decimal
    gap_amount: Decimal
    importance: Decimal
    resources: tuple[LearningResourceSummary, ...]


@dataclass(frozen=True)
class LearningPlan:
    """
    Combined WBS 5.7 service output for later REST serialization.
    """

    student_profile_id: int
    career_id: int
    career_name: str
    readiness_result: CareerReadinessResult
    suggestions: tuple[LearningSuggestion, ...]
    roadmap_steps: tuple[RoadmapStep, ...]


def get_unresolved_skill_gaps(
    readiness_result: CareerReadinessResult,
) -> tuple[SkillGapResult, ...]:
    """
    Return WBS 5.5 gaps that require learning action.

    The input order from WBS 5.5 is preserved.
    """

    return tuple(
        gap
        for gap in readiness_result.skill_gaps
        if gap.gap_status in UNRESOLVED_GAP_STATUSES
    )


def load_active_learning_resources_by_skill(
    *,
    skill_ids: Iterable[int],
) -> dict[int, tuple[LearningResourceSummary, ...]]:
    """
    Load active controlled learning resources for canonical Skills.

    Returns an entry for each supplied Skill ID. Skills without
    matching active resources map to an empty tuple.
    """

    ordered_skill_ids = tuple(
        dict.fromkeys(
            skill_ids
        )
    )

    if not ordered_skill_ids:
        return {}

    resources_by_skill = {
        skill_id: []
        for skill_id in ordered_skill_ids
    }

    resource_rows = (
        LearningResource.objects
        .filter(
            is_active=True,
            skill_links__skill_id__in=(
                ordered_skill_ids
            ),
        )
        .values(
            "skill_links__skill_id",
            "id",
            "title",
            "provider",
            "url",
            "resource_type",
            "description",
        )
        .order_by(
            "skill_links__skill_id",
            "title",
            "provider",
            "id",
        )
    )

    for row in resource_rows:
        skill_id = row[
            "skill_links__skill_id"
        ]

        resources_by_skill[
            skill_id
        ].append(
            LearningResourceSummary(
                id=row["id"],
                title=row["title"],
                provider=row["provider"],
                url=row["url"],
                resource_type=row[
                    "resource_type"
                ],
                description=row[
                    "description"
                ],
            )
        )

    return {
        skill_id: tuple(resources)
        for skill_id, resources
        in resources_by_skill.items()
    }


def build_learning_suggestions(
    *,
    unresolved_gaps: Iterable[SkillGapResult],
    resources_by_skill: dict[int, tuple[LearningResourceSummary, ...]],
) -> tuple[LearningSuggestion, ...]:
    """
    Build structured suggestions while preserving WBS 5.5 gap order.
    """

    return tuple(
        LearningSuggestion(
            priority=index,
            skill_id=gap.skill_id,
            skill_name=gap.skill_name,
            gap_status=gap.gap_status,
            current_proficiency=(
                gap.student_proficiency_level
            ),
            current_score=(
                gap.student_proficiency_score
            ),
            required_level=gap.required_level,
            gap_amount=gap.gap_amount,
            importance=gap.importance,
            resources=resources_by_skill.get(
                gap.skill_id,
                (),
            ),
        )
        for index, gap
        in enumerate(
            unresolved_gaps,
            start=1,
        )
    )


def build_roadmap_steps(
    *,
    suggestions: Iterable[LearningSuggestion],
) -> tuple[RoadmapStep, ...]:
    """
    Build ordered roadmap steps from learning suggestions.

    Step order is the WBS 5.5 unresolved-gap order.
    """

    return tuple(
        RoadmapStep(
            step_number=index,
            skill_id=suggestion.skill_id,
            skill_name=suggestion.skill_name,
            gap_status=suggestion.gap_status,
            current_proficiency=(
                suggestion.current_proficiency
            ),
            current_score=(
                suggestion.current_score
            ),
            required_level=(
                suggestion.required_level
            ),
            gap_amount=suggestion.gap_amount,
            importance=suggestion.importance,
            resources=suggestion.resources,
        )
        for index, suggestion
        in enumerate(
            suggestions,
            start=1,
        )
    )


def generate_learning_plan(
    *,
    student_profile_id: int,
    career_id: int,
) -> LearningPlan:
    """
    Generate WBS 5.7 learning suggestions and roadmap steps.

    The service delegates selected-Career readiness and gap ordering
    to WBS 5.5, then attaches active database-backed learning
    resources to unresolved canonical Skills.
    """

    readiness_result = (
        readiness_scoring
        .calculate_selected_career_readiness(
            student_profile_id=(
                student_profile_id
            ),
            career_id=career_id,
        )
    )

    unresolved_gaps = (
        get_unresolved_skill_gaps(
            readiness_result
        )
    )

    resources_by_skill = (
        load_active_learning_resources_by_skill(
            skill_ids=(
                gap.skill_id
                for gap in unresolved_gaps
            )
        )
    )

    suggestions = build_learning_suggestions(
        unresolved_gaps=unresolved_gaps,
        resources_by_skill=resources_by_skill,
    )

    roadmap_steps = build_roadmap_steps(
        suggestions=suggestions
    )

    return LearningPlan(
        student_profile_id=student_profile_id,
        career_id=readiness_result.career_id,
        career_name=readiness_result.career_name,
        readiness_result=readiness_result,
        suggestions=suggestions,
        roadmap_steps=roadmap_steps,
    )

