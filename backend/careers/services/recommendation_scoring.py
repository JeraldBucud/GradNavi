"""
Deterministic career recommendation scoring for GradNavi.

WBS 5.3 uses canonical Skill matches and source-backed O*NET
normalized Importance values to calculate Career-fit scores.

Student proficiency is intentionally excluded from this service.
Proficiency-based readiness belongs to WBS 5.5.
"""

from dataclasses import dataclass, field, replace
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Iterable

from django.db.models import Q

from careers.models import (
    Career,
    CareerSkillEvidence,
    ReferenceDataset,
    ReviewStatus,
)
from profiles.models import StudentSkill


SCORE_MINIMUM = Decimal("0")
SCORE_MAXIMUM = Decimal("100")
SCORE_QUANTUM = Decimal("0.01")

ONET_SOURCE_NAME = "O*NET Database"
ESCO_SOURCE_NAME = "ESCO"

ONET_SOFTWARE_SOURCE_DOMAIN = (
    "onet_software_skills"
)

ESCO_ESSENTIAL_RELATION = "essential"
ESCO_OPTIONAL_RELATION = "optional"

ONET_NUMERICAL_SOURCE_DOMAINS = (
    "onet_essential_skills",
    "onet_knowledge",
    "onet_transferable_skills",
)


class ScoreStatus(str, Enum):
    """
    Describes whether a Career received a valid WBS 5.3 score.

    SCORED
        The Career has enough numerical O*NET evidence for scoring.

    INSUFFICIENT_PROFILE
        The Student has no Skills available for Career comparison.

    INSUFFICIENT_EVIDENCE
        The Career has no eligible numerical O*NET evidence.
    """

    SCORED = "scored"
    INSUFFICIENT_PROFILE = "insufficient_profile"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class WeightedCompetency:
    """
    One CareerSkill with source-backed numerical Importance.

    career_skill_id
        Identifies the CareerSkill relationship.

    skill_id
        Canonical GradNavi Skill identifier.

    skill_name
        Human-readable Skill name used in explanations.

    importance
        O*NET normalized Importance value from 0 to 100.
    """

    career_skill_id: int
    skill_id: int
    skill_name: str
    importance: Decimal


@dataclass(frozen=True)
class RecommendationResult:
    """
    Structured result returned by the WBS 5.3 scoring service.

    The service returns structured data instead of frontend text.
    WBS 5.4 will later decide how this data is serialized through
    the Career Recommendation API.
    """

    career_id: int
    career_name: str
    score_status: ScoreStatus

    recommendation_score: Decimal | None = None
    rank: int | None = None

    matched_weight: Decimal = Decimal("0")
    total_weight: Decimal = Decimal("0")

    matched_competencies: tuple[str, ...] = field(
        default_factory=tuple
    )

    missing_competencies: tuple[str, ...] = field(
        default_factory=tuple
    )

    matched_technologies: tuple[str, ...] = field(
        default_factory=tuple
    )

    esco_essential_skills: tuple[str, ...] = field(
        default_factory=tuple
    )

    esco_optional_skills: tuple[str, ...] = field(
        default_factory=tuple
    )

    esco_essential_matches: int = 0
    esco_optional_matches: int = 0


@dataclass(frozen=True)
class CareerExplanationEvidence:
    """
    Non-numerical evidence used to explain a Career match.

    These values do not change recommendation_score or rank.
    """

    matched_technologies: tuple[str, ...] = field(
        default_factory=tuple
    )

    esco_essential_skills: tuple[str, ...] = field(
        default_factory=tuple
    )

    esco_optional_skills: tuple[str, ...] = field(
        default_factory=tuple
    )


def load_student_skill_ids(
    *,
    student_profile_id: int,
) -> tuple[int, ...]:
    """
    Load canonical Skill IDs assigned to one Student Profile.

    This function performs a database read only.

    Proficiency is intentionally not loaded because WBS 5.3
    Career-fit scoring checks whether the canonical Skill exists.
    WBS 5.5 owns proficiency-based readiness scoring.
    """

    return tuple(
        StudentSkill.objects
        .filter(
            student_profile_id=student_profile_id
        )
        .order_by(
            "skill_id"
        )
        .values_list(
            "skill_id",
            flat=True,
        )
    )


def load_weighted_competencies_by_career(
    *,
    career_ids: Iterable[int],
) -> dict[int, tuple[WeightedCompetency, ...]]:
    """
    Load eligible numerical O*NET evidence for multiple Careers.

    One database query loads evidence for all supplied Careers.

    Eligible Version 1 evidence must satisfy these rules:

    - CareerSkill review status is approved.
    - Reference dataset is active.
    - Source is O*NET Database.
    - Source domain is approved for numerical scoring.
    - normalized_importance is present.
    - Evidence is not marked not relevant.
    - Evidence is not marked recommend suppress.

    Duplicate numerical evidence stays visible so the pure
    scoring function rejects accidental double counting.
    """

    unique_career_ids = tuple(
        dict.fromkeys(
            career_ids
        )
    )

    if not unique_career_ids:
        return {}

    grouped = {
        career_id: []
        for career_id
        in unique_career_ids
    }

    evidence_rows = (
        CareerSkillEvidence.objects
        .select_related(
            "career_skill__skill",
        )
        .filter(
            career_skill__career_id__in=(
                unique_career_ids
            ),
            career_skill__review_status=(
                ReviewStatus.APPROVED
            ),
            dataset__status=(
                ReferenceDataset.Status.ACTIVE
            ),
            dataset__source__name=(
                ONET_SOURCE_NAME
            ),
            source_domain__in=(
                ONET_NUMERICAL_SOURCE_DOMAINS
            ),
            normalized_importance__isnull=False,
            not_relevant=False,
        )
        .exclude(
            recommend_suppress=True
        )
        .order_by(
            "career_skill__career_id",
            "career_skill_id",
            "id",
        )
    )

    for evidence in evidence_rows:
        career_id = (
            evidence
            .career_skill
            .career_id
        )

        grouped[
            career_id
        ].append(
            WeightedCompetency(
                career_skill_id=(
                    evidence.career_skill_id
                ),
                skill_id=(
                    evidence
                    .career_skill
                    .skill_id
                ),
                skill_name=(
                    evidence
                    .career_skill
                    .skill
                    .name
                ),
                importance=(
                    evidence.normalized_importance
                ),
            )
        )

    return {
        career_id: tuple(
            competencies
        )
        for career_id, competencies
        in grouped.items()
    }


def load_weighted_competencies(
    *,
    career_id: int,
) -> tuple[WeightedCompetency, ...]:
    """
    Load eligible numerical O*NET evidence for one Career.

    This wrapper uses the multi-Career loader so the evidence
    eligibility rules stay in one location.
    """

    grouped = (
        load_weighted_competencies_by_career(
            career_ids=(
                career_id,
            )
        )
    )

    return grouped.get(
        career_id,
        (),
    )


def load_explanation_evidence_by_career(
    *,
    career_ids: Iterable[int],
    student_skill_ids: Iterable[int],
) -> dict[int, CareerExplanationEvidence]:
    """
    Load matched non-numerical evidence for multiple Careers.

    Version 1 explanation evidence includes:

    - O*NET software technologies.
    - ESCO essential relationships.
    - ESCO optional relationships.

    Only canonical Skills already present in the Student Profile
    are returned as matches.

    This evidence does not affect the numerical Career-fit score.
    """

    unique_career_ids = tuple(
        dict.fromkeys(
            career_ids
        )
    )

    student_skill_id_set = frozenset(
        student_skill_ids
    )

    if (
        not unique_career_ids
        or not student_skill_id_set
    ):
        return {
            career_id: CareerExplanationEvidence()
            for career_id
            in unique_career_ids
        }

    grouped = {
        career_id: {
            "technologies": set(),
            "essential": set(),
            "optional": set(),
        }
        for career_id
        in unique_career_ids
    }

    evidence_rows = (
        CareerSkillEvidence.objects
        .select_related(
            "career_skill__skill",
            "dataset__source",
        )
        .filter(
            career_skill__career_id__in=(
                unique_career_ids
            ),
            career_skill__skill_id__in=(
                student_skill_id_set
            ),
            career_skill__review_status=(
                ReviewStatus.APPROVED
            ),
            dataset__status=(
                ReferenceDataset.Status.ACTIVE
            ),
            not_relevant=False,
        )
        .filter(
            Q(
                dataset__source__name=(
                    ONET_SOURCE_NAME
                ),
                source_domain=(
                    ONET_SOFTWARE_SOURCE_DOMAIN
                ),
            )
            |
            Q(
                dataset__source__name=(
                    ESCO_SOURCE_NAME
                ),
                source_relation__in=(
                    ESCO_ESSENTIAL_RELATION,
                    ESCO_OPTIONAL_RELATION,
                ),
            )
        )
        .exclude(
            recommend_suppress=True
        )
        .order_by(
            "career_skill__career_id",
            "career_skill__skill__name",
            "id",
        )
    )

    for evidence in evidence_rows:
        career_id = (
            evidence
            .career_skill
            .career_id
        )

        skill_name = (
            evidence
            .career_skill
            .skill
            .name
        )

        source_name = (
            evidence
            .dataset
            .source
            .name
        )

        if (
            source_name
            == ONET_SOURCE_NAME
            and evidence.source_domain
            == ONET_SOFTWARE_SOURCE_DOMAIN
        ):
            grouped[
                career_id
            ][
                "technologies"
            ].add(
                skill_name
            )

        elif (
            source_name
            == ESCO_SOURCE_NAME
            and evidence.source_relation
            == ESCO_ESSENTIAL_RELATION
        ):
            grouped[
                career_id
            ][
                "essential"
            ].add(
                skill_name
            )

        elif (
            source_name
            == ESCO_SOURCE_NAME
            and evidence.source_relation
            == ESCO_OPTIONAL_RELATION
        ):
            grouped[
                career_id
            ][
                "optional"
            ].add(
                skill_name
            )

    return {
        career_id: CareerExplanationEvidence(
            matched_technologies=tuple(
                sorted(
                    values[
                        "technologies"
                    ]
                )
            ),
            esco_essential_skills=tuple(
                sorted(
                    values[
                        "essential"
                    ]
                )
            ),
            esco_optional_skills=tuple(
                sorted(
                    values[
                        "optional"
                    ]
                )
            ),
        )
        for career_id, values
        in grouped.items()
    }


def calculate_career_fit(
    *,
    career_id: int,
    career_name: str,
    student_skill_ids: Iterable[int],
    weighted_competencies: Iterable[WeightedCompetency],
) -> RecommendationResult:
    """
    Calculate the WBS 5.3 Career-fit score for one Career.

    Formula:

        recommendation_score
            =
        matched_weight / total_weight * 100

    A canonical Skill matches when the Student Skill ID equals the
    CareerSkill Skill ID.

    Student proficiency does not affect this calculation.
    """

    student_skill_id_set = frozenset(
        student_skill_ids
    )

    competencies = tuple(
        weighted_competencies
    )

    # A Student with no Skills does not have enough profile data
    # for a meaningful Career recommendation.
    if not student_skill_id_set:
        return RecommendationResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_PROFILE
            ),
        )

    # A Career without numerical O*NET evidence does not receive
    # a fabricated numerical score.
    if not competencies:
        return RecommendationResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
        )

    matched_weight = Decimal("0")
    total_weight = Decimal("0")

    matched_competencies = []
    missing_competencies = []

    seen_career_skill_ids = set()

    for competency in competencies:
        # The same CareerSkill must never contribute twice.
        if (
            competency.career_skill_id
            in seen_career_skill_ids
        ):
            raise ValueError(
                "Duplicate numerical CareerSkill evidence "
                "was supplied to the scoring calculation."
            )

        seen_career_skill_ids.add(
            competency.career_skill_id
        )

        importance = competency.importance

        # Dataset 1.0 normalized Importance values must stay
        # inside the approved 0 to 100 range.
        if (
            importance < SCORE_MINIMUM
            or importance > SCORE_MAXIMUM
        ):
            raise ValueError(
                "CareerSkill Importance must be "
                "between 0 and 100."
            )

        total_weight += importance

        if (
            competency.skill_id
            in student_skill_id_set
        ):
            matched_weight += importance

            matched_competencies.append(
                competency.skill_name
            )

        else:
            missing_competencies.append(
                competency.skill_name
            )

    # Numerical evidence with a total weight of zero does not
    # produce a meaningful weighted ratio.
    if total_weight == Decimal("0"):
        return RecommendationResult(
            career_id=career_id,
            career_name=career_name,
            score_status=(
                ScoreStatus.INSUFFICIENT_EVIDENCE
            ),
        )

    unrounded_score = (
        matched_weight
        / total_weight
        * SCORE_MAXIMUM
    )

    recommendation_score = (
        unrounded_score.quantize(
            SCORE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
    )

    return RecommendationResult(
        career_id=career_id,
        career_name=career_name,
        score_status=ScoreStatus.SCORED,
        recommendation_score=(
            recommendation_score
        ),
        matched_weight=matched_weight,
        total_weight=total_weight,
        matched_competencies=tuple(
            sorted(
                matched_competencies
            )
        ),
        missing_competencies=tuple(
            sorted(
                missing_competencies
            )
        ),
    )


def rank_recommendation_results(
    results: Iterable[RecommendationResult],
) -> tuple[RecommendationResult, ...]:
    """
    Rank Career recommendation results deterministically.

    Rules:

    1. Scored Careers rank before unscored Careers.
    2. Scored Careers use the unrounded weighted ratio.
    3. Higher weighted ratio ranks first.
    4. Equal ratios use Career name alphabetically.
    5. Equal names use Career ID ascending.
    6. Unscored Careers receive rank=None.

    The displayed recommendation_score is not used for ranking.
    """

    result_list = tuple(
        results
    )

    scored_results = []
    unscored_results = []

    for result in result_list:
        if (
            result.score_status
            == ScoreStatus.SCORED
        ):
            if (
                result.total_weight
                <= Decimal("0")
            ):
                raise ValueError(
                    "A scored Career must have "
                    "total_weight greater than zero."
                )

            if (
                result.recommendation_score
                is None
            ):
                raise ValueError(
                    "A scored Career must have "
                    "a recommendation score."
                )

            scored_results.append(
                result
            )

        else:
            unscored_results.append(
                result
            )

    def ranking_ratio(
        result: RecommendationResult,
    ) -> Decimal:
        """
        Return the exact weighted coverage ratio.

        This value is intentionally calculated from the
        unrounded matched and total weights.
        """

        return (
            result.matched_weight
            / result.total_weight
        )

    scored_results.sort(
        key=lambda result: (
            -ranking_ratio(
                result
            ),
            result.career_name.casefold(),
            result.career_id,
        )
    )

    ranked_results = tuple(
        replace(
            result,
            rank=index,
        )
        for index, result
        in enumerate(
            scored_results,
            start=1,
        )
    )

    unscored_results.sort(
        key=lambda result: (
            result.career_name.casefold(),
            result.career_id,
        )
    )

    unranked_results = tuple(
        replace(
            result,
            rank=None,
        )
        for result in unscored_results
    )

    return (
        ranked_results
        + unranked_results
    )


def generate_recommendations(
    *,
    student_profile_id: int,
) -> tuple[RecommendationResult, ...]:
    """
    Generate deterministic WBS 5.3 recommendations.

    The service:

    1. Loads the Student's canonical Skill identifiers.
    2. Loads all active Careers.
    3. Loads eligible numerical evidence for those Careers.
    4. Calculates one Career-fit result per Career.
    5. Applies deterministic ranking.

    This function performs database reads only.
    """

    student_skill_ids = (
        load_student_skill_ids(
            student_profile_id=(
                student_profile_id
            )
        )
    )

    careers = tuple(
        Career.objects
        .filter(
            active=True
        )
        .order_by(
            "name",
            "id",
        )
        .only(
            "id",
            "name",
        )
    )

    if not careers:
        return ()

    # A Student without Skills does not have enough profile
    # information for meaningful Career-fit ranking.
    if not student_skill_ids:
        results = tuple(
            RecommendationResult(
                career_id=career.id,
                career_name=career.name,
                score_status=(
                    ScoreStatus.INSUFFICIENT_PROFILE
                ),
            )
            for career in careers
        )

        return rank_recommendation_results(
            results
        )

    career_ids = tuple(
        career.id
        for career in careers
    )

    competencies_by_career = (
        load_weighted_competencies_by_career(
            career_ids=career_ids
        )
    )

    explanation_by_career = (
        load_explanation_evidence_by_career(
            career_ids=career_ids,
            student_skill_ids=(
                student_skill_ids
            ),
        )
    )

    results = []

    for career in careers:
        result = calculate_career_fit(
            career_id=career.id,
            career_name=career.name,
            student_skill_ids=(
                student_skill_ids
            ),
            weighted_competencies=(
                competencies_by_career.get(
                    career.id,
                    (),
                )
            ),
        )

        explanation = (
            explanation_by_career.get(
                career.id,
                CareerExplanationEvidence(),
            )
        )

        result = replace(
            result,
            matched_technologies=(
                explanation
                .matched_technologies
            ),
            esco_essential_skills=(
                explanation
                .esco_essential_skills
            ),
            esco_optional_skills=(
                explanation
                .esco_optional_skills
            ),
            esco_essential_matches=len(
                explanation
                .esco_essential_skills
            ),
            esco_optional_matches=len(
                explanation
                .esco_optional_skills
            ),
        )

        results.append(
            result
        )

    return rank_recommendation_results(
        results
    )
