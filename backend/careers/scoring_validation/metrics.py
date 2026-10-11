"""
Generic ranking metrics for GradNavi scoring validation.

These functions do not know anything about the GradNavi scoring
formula. They evaluate only where an expected Career appears in a
ranked list.

Keeping metrics independent means the same evaluation rules can be
used fairly for:

- Current WBS 5.3 Version 1 scoring.
- Candidate scoring model A.
- Candidate scoring model B.
- Any later calibrated scoring model.
"""

from dataclasses import dataclass
from math import log2
from typing import Iterable


@dataclass(frozen=True)
class RankingMetrics:
    """
    Aggregate ranking quality for a collection of benchmark cases.

    case_count
        Number of benchmark profiles evaluated.

    hit_at_1
        Percentage of cases where the expected Career ranked first.

    hit_at_3
        Percentage of cases where the expected Career appeared in
        the top three results.

    hit_at_5
        Percentage of cases where the expected Career appeared in
        the top five results.

    mean_reciprocal_rank
        Average reciprocal rank of the expected Career.

        Rank 1 -> 1.0
        Rank 2 -> 0.5
        Rank 3 -> 0.333...
        Missing -> 0.0

    ndcg_at_5
        Normalized discounted cumulative gain at rank five.

        Because each synthetic benchmark profile has one known
        target Career, this rewards correct Careers more strongly
        when they appear nearer the top of the ranking.
    """

    case_count: int

    hit_at_1: float
    hit_at_3: float
    hit_at_5: float

    mean_reciprocal_rank: float
    ndcg_at_5: float


def find_target_rank(
    *,
    ranked_career_ids: Iterable[int],
    target_career_id: int,
) -> int | None:
    """
    Return the one-based rank of the expected Career.

    Example:

        ranked_career_ids = [8, 3, 12]
        target_career_id = 3

    Result:

        2

    If the target Career does not occur, return None.
    """

    if target_career_id <= 0:
        raise ValueError(
            "target_career_id must be greater than zero."
        )

    for rank, career_id in enumerate(
        ranked_career_ids,
        start=1,
    ):
        if career_id == target_career_id:
            return rank

    return None


def hit_at_k(
    *,
    rank: int | None,
    k: int,
) -> float:
    """
    Return 1.0 when the expected Career appears within top-k.

    Otherwise return 0.0.
    """

    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    if rank is None:
        return 0.0

    if rank <= 0:
        raise ValueError(
            "rank must be greater than zero."
        )

    return 1.0 if rank <= k else 0.0


def reciprocal_rank(
    rank: int | None,
) -> float:
    """
    Return the reciprocal rank of one benchmark result.

    Examples:

        Rank 1 -> 1.0
        Rank 2 -> 0.5
        Rank 4 -> 0.25
        Missing -> 0.0
    """

    if rank is None:
        return 0.0

    if rank <= 0:
        raise ValueError(
            "rank must be greater than zero."
        )

    return 1.0 / rank


def ndcg_at_k(
    *,
    rank: int | None,
    k: int,
) -> float:
    """
    Calculate NDCG@k for a benchmark case with one relevant Career.

    The ideal result places the expected Career at rank 1.

    Rank 1 therefore scores 1.0.

    Lower ranks receive progressively smaller values because the
    correct Career is less useful when it appears farther down the
    recommendation list.

    A Career outside top-k receives 0.0.
    """

    if k <= 0:
        raise ValueError(
            "k must be greater than zero."
        )

    if rank is None:
        return 0.0

    if rank <= 0:
        raise ValueError(
            "rank must be greater than zero."
        )

    if rank > k:
        return 0.0

    return 1.0 / log2(rank + 1)


def calculate_ranking_metrics(
    target_ranks: Iterable[int | None],
) -> RankingMetrics:
    """
    Aggregate ranking metrics across benchmark cases.

    target_ranks contains the observed rank of the expected Career
    for every benchmark profile.

    None means the expected Career was not present in the ranked
    result set.
    """

    ranks = tuple(target_ranks)

    if not ranks:
        raise ValueError(
            "At least one benchmark rank is required."
        )

    for rank in ranks:
        if rank is not None and rank <= 0:
            raise ValueError(
                "Benchmark ranks must be greater than zero."
            )

    case_count = len(ranks)

    hit_1_total = sum(
        hit_at_k(
            rank=rank,
            k=1,
        )
        for rank in ranks
    )

    hit_3_total = sum(
        hit_at_k(
            rank=rank,
            k=3,
        )
        for rank in ranks
    )

    hit_5_total = sum(
        hit_at_k(
            rank=rank,
            k=5,
        )
        for rank in ranks
    )

    reciprocal_rank_total = sum(
        reciprocal_rank(rank)
        for rank in ranks
    )

    ndcg_5_total = sum(
        ndcg_at_k(
            rank=rank,
            k=5,
        )
        for rank in ranks
    )

    return RankingMetrics(
        case_count=case_count,
        hit_at_1=(
            hit_1_total
            / case_count
        ),
        hit_at_3=(
            hit_3_total
            / case_count
        ),
        hit_at_5=(
            hit_5_total
            / case_count
        ),
        mean_reciprocal_rank=(
            reciprocal_rank_total
            / case_count
        ),
        ndcg_at_5=(
            ndcg_5_total
            / case_count
        ),
    )