from dataclasses import dataclass

from django.db.models import Q

from careers.models import (
    Career,
    StudentCareerEvaluation,
)
from careers.services.recommendation_cache import (
    RecommendationCacheKey,
    build_recommendation_cache_key,
    get_valid_recommendation_snapshot,
)


RECOMMENDED_CAREER_LIMIT = 7

EXPLORE_STATUS_ALL = "all"

EXPLORE_STATUS_RECOMMENDED = (
    "recommended"
)

EXPLORE_STATUS_EVALUATED = (
    "evaluated"
)

EXPLORE_STATUS_NOT_EVALUATED = (
    "not_evaluated"
)

EXPLORE_STATUSES = {
    EXPLORE_STATUS_ALL,
    EXPLORE_STATUS_RECOMMENDED,
    EXPLORE_STATUS_EVALUATED,
    EXPLORE_STATUS_NOT_EVALUATED,
}



class ExploreCareerError(Exception):
    """
    Base Explore Careers service error.
    """


class ExploreCareerNotFoundError(
    ExploreCareerError
):
    """
    Raised when the selected Career does not exist.
    """


class ExploreCareerNotAvailableError(
    ExploreCareerError
):
    """
    Raised when the selected Career is inactive.
    """


class CareerEvaluationSnapshotUnavailableError(
    ExploreCareerError
):
    """
    Raised when no current recommendation snapshot exists.
    """


class CareerEvaluationResultUnavailableError(
    ExploreCareerError
):
    """
    Raised when the current recommendation snapshot
    does not contain the selected Career.
    """


@dataclass(frozen=True)
class ExploreCareerItem:
    career_id: int
    career_name: str

    description: str
    category: str

    status: str

    recommended: bool
    evaluated: bool

    recommendation_rank: int | None
    match_score: str | None


def _safe_int(
    value,
) -> int | None:
    try:
        return int(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def _normalise_status(
    value,
) -> str:
    status = (
        str(
            value
            or EXPLORE_STATUS_ALL
        )
        .strip()
        .casefold()
    )

    if status not in EXPLORE_STATUSES:
        raise ValueError(
            "Unsupported Explore Careers status."
        )

    return status


def _recommendation_rows(
    snapshot,
) -> tuple[dict, ...]:
    if snapshot is None:
        return ()

    payload = snapshot.payload

    if not isinstance(
        payload,
        dict,
    ):
        return ()

    recommendations = (
        payload.get(
            "recommendations"
        )
    )

    if not isinstance(
        recommendations,
        list,
    ):
        return ()

    return tuple(
        row
        for row in recommendations
        if isinstance(
            row,
            dict,
        )
    )


def build_recommendation_map(
    snapshot,
) -> dict[int, dict]:
    result = {}

    for row in _recommendation_rows(
        snapshot
    ):
        career_id = _safe_int(
            row.get(
                "career_id"
            )
        )

        if career_id is None:
            continue

        result[
            career_id
        ] = row

    return result


def load_recommended_career_ids(
    snapshot,
) -> tuple[int, ...]:
    rows = list(
        _recommendation_rows(
            snapshot
        )
    )

    rows.sort(
        key=lambda row: (
            _safe_int(
                row.get(
                    "rank"
                )
            )
            or 999999,
            str(
                row.get(
                    "career_name",
                    "",
                )
            ).casefold(),
            _safe_int(
                row.get(
                    "career_id"
                )
            )
            or 999999,
        )
    )

    career_ids = []

    for row in rows:
        career_id = _safe_int(
            row.get(
                "career_id"
            )
        )

        if career_id is None:
            continue

        career_ids.append(
            career_id
        )

        if (
            len(
                career_ids
            )
            >= RECOMMENDED_CAREER_LIMIT
        ):
            break

    return tuple(
        career_ids
    )


def get_valid_student_career_evaluation(
    *,
    student_profile,
    career,
    cache_key: RecommendationCacheKey | None = None,
) -> StudentCareerEvaluation | None:
    if cache_key is None:
        cache_key = (
            build_recommendation_cache_key(
                student_profile=(
                    student_profile
                ),
            )
        )

    evaluation = (
        StudentCareerEvaluation.objects
        .filter(
            student_profile=(
                student_profile
            ),
            career=career,
        )
        .first()
    )

    if evaluation is None:
        return None

    if (
        evaluation.profile_fingerprint
        != cache_key.profile_fingerprint
    ):
        return None

    if (
        evaluation.reference_fingerprint
        != cache_key.reference_fingerprint
    ):
        return None

    if (
        evaluation.scoring_version
        != cache_key.scoring_version
    ):
        return None

    return evaluation


def load_valid_student_career_evaluations(
    *,
    student_profile,
    cache_key: RecommendationCacheKey | None = None,
) -> dict[
    int,
    StudentCareerEvaluation,
]:
    if cache_key is None:
        cache_key = (
            build_recommendation_cache_key(
                student_profile=(
                    student_profile
                ),
            )
        )

    evaluations = (
        StudentCareerEvaluation.objects
        .filter(
            student_profile=(
                student_profile
            ),
            profile_fingerprint=(
                cache_key
                .profile_fingerprint
            ),
            reference_fingerprint=(
                cache_key
                .reference_fingerprint
            ),
            scoring_version=(
                cache_key
                .scoring_version
            ),
            career__active=True,
        )
        .select_related(
            "career"
        )
        .order_by(
            "career__name",
            "career_id",
        )
    )

    return {
        evaluation.career_id:
            evaluation
        for evaluation
        in evaluations
    }



def evaluate_career_from_snapshot(
    *,
    student_profile,
    career_id: int,
) -> StudentCareerEvaluation:
    """
    Save one explicit Student Career evaluation.

    The current valid recommendation snapshot already
    contains the composite result for every active Career.

    This function reuses that result and stores only the
    selected Career evaluation.
    """

    if career_id <= 0:
        raise ValueError(
            "career_id must be greater than zero."
        )

    career = (
        Career.objects
        .filter(
            id=career_id
        )
        .only(
            "id",
            "name",
            "active",
        )
        .first()
    )

    if career is None:
        raise ExploreCareerNotFoundError(
            f"Career {career_id} does not exist."
        )

    if not career.active:
        raise ExploreCareerNotAvailableError(
            f"Career {career_id} is not active."
        )

    cache_key = (
        build_recommendation_cache_key(
            student_profile=student_profile,
        )
    )

    snapshot = (
        get_valid_recommendation_snapshot(
            student_profile=student_profile,
            cache_key=cache_key,
        )
    )

    if snapshot is None:
        raise (
            CareerEvaluationSnapshotUnavailableError(
                "A current Career Recommendation "
                "snapshot is required."
            )
        )

    recommendation = (
        build_recommendation_map(
            snapshot
        )
        .get(
            career.id
        )
    )

    if recommendation is None:
        raise (
            CareerEvaluationResultUnavailableError(
                "The current recommendation snapshot "
                "does not contain the selected Career."
            )
        )

    evaluation, _ = (
        StudentCareerEvaluation.objects
        .update_or_create(
            student_profile=student_profile,
            career=career,
            defaults={
                "profile_fingerprint": (
                    cache_key
                    .profile_fingerprint
                ),
                "reference_fingerprint": (
                    cache_key
                    .reference_fingerprint
                ),
                "scoring_version": (
                    cache_key
                    .scoring_version
                ),
                "payload": recommendation,
            },
        )
    )

    return evaluation


def list_explore_career_categories():
    categories = (
        Career.objects
        .filter(
            active=True,
        )
        .exclude(
            category="",
        )
        .values_list(
            "category",
            flat=True,
        )
        .distinct()
        .order_by(
            "category"
        )
    )

    return tuple(
        categories
    )


def list_explore_careers(
    *,
    student_profile,
    search: str = "",
    category: str = "",
    status: str = EXPLORE_STATUS_ALL,
) -> tuple[
    ExploreCareerItem,
    ...
]:
    normalised_status = (
        _normalise_status(
            status
        )
    )

    queryset = (
        Career.objects
        .filter(
            active=True,
        )
    )

    normalised_search = (
        str(
            search
            or ""
        )
        .strip()
    )

    if normalised_search:
        queryset = queryset.filter(
            Q(
                name__icontains=(
                    normalised_search
                )
            )
            | Q(
                description__icontains=(
                    normalised_search
                )
            )
            | Q(
                category__icontains=(
                    normalised_search
                )
            )
        )

    normalised_category = (
        str(
            category
            or ""
        )
        .strip()
    )

    if normalised_category:
        queryset = queryset.filter(
            category__iexact=(
                normalised_category
            )
        )

    careers = tuple(
        queryset.order_by(
            "name",
            "id",
        )
    )

    cache_key = (
        build_recommendation_cache_key(
            student_profile=(
                student_profile
            ),
        )
    )

    recommendation_snapshot = (
        get_valid_recommendation_snapshot(
            student_profile=(
                student_profile
            ),
            cache_key=cache_key,
        )
    )

    recommendation_map = (
        build_recommendation_map(
            recommendation_snapshot
        )
    )

    recommended_ids = set(
        load_recommended_career_ids(
            recommendation_snapshot
        )
    )

    evaluations = (
        load_valid_student_career_evaluations(
            student_profile=(
                student_profile
            ),
            cache_key=cache_key,
        )
    )

    items = []

    for career in careers:
        recommended = (
            career.id
            in recommended_ids
        )

        evaluation = (
            evaluations.get(
                career.id
            )
        )

        evaluated = (
            evaluation is not None
        )

        if recommended:
            item_status = (
                EXPLORE_STATUS_RECOMMENDED
            )

        elif evaluated:
            item_status = (
                EXPLORE_STATUS_EVALUATED
            )

        else:
            item_status = (
                EXPLORE_STATUS_NOT_EVALUATED
            )

        if (
            normalised_status
            != EXPLORE_STATUS_ALL
            and
            item_status
            != normalised_status
        ):
            continue

        result_payload = {}

        if recommended:
            result_payload = (
                recommendation_map.get(
                    career.id,
                    {},
                )
            )

        elif evaluated:
            result_payload = (
                evaluation.payload
                if isinstance(
                    evaluation.payload,
                    dict,
                )
                else {}
            )

        rank = None

        if recommended:
            rank = _safe_int(
                result_payload.get(
                    "rank"
                )
            )

        match_score = None

        if (
            recommended
            or evaluated
        ):
            raw_score = (
                result_payload.get(
                    "recommendation_score"
                )
            )

            if raw_score is not None:
                match_score = str(
                    raw_score
                )

        items.append(
            ExploreCareerItem(
                career_id=(
                    career.id
                ),
                career_name=(
                    career.name
                ),
                description=(
                    career.description
                ),
                category=(
                    career.category
                ),
                status=(
                    item_status
                ),
                recommended=(
                    recommended
                ),
                evaluated=(
                    evaluated
                ),
                recommendation_rank=(
                    rank
                ),
                match_score=(
                    match_score
                ),
            )
        )

    return tuple(
        items
    )


def list_guidance_careers(
    *,
    student_profile,
) -> tuple[
    ExploreCareerItem,
    ...
]:
    items = list(
        list_explore_careers(
            student_profile=(
                student_profile
            ),
        )
    )

    eligible = [
        item
        for item in items
        if (
            item.recommended
            or item.evaluated
        )
    ]

    eligible.sort(
        key=lambda item: (
            0
            if item.recommended
            else 1,
            item.recommendation_rank
            or 999999,
            item.career_name.casefold(),
            item.career_id,
        )
    )

    return tuple(
        eligible
    )
