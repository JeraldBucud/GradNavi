"""
O*NET occupation-group helpers for GradNavi scoring validation.

Several GradNavi Careers intentionally map to the same O*NET
occupation. Those Careers therefore share identical O*NET numerical
evidence and cannot be distinguished by an O*NET-only scoring model.

This module lets benchmarks evaluate both:

1. Exact GradNavi Career ranking.
2. O*NET occupation-group ranking.

No production scoring behaviour is changed.
"""

from dataclasses import dataclass

from careers.models import (
    Career,
    CareerExternalMapping,
    ReferenceDataset,
    ReviewStatus,
)


ONET_SOURCE_NAME = "O*NET Database"


@dataclass(frozen=True)
class OccupationGroup:
    """
    One approved O*NET occupation and its GradNavi Careers.
    """

    external_id: str

    external_title: str

    career_ids: tuple[int, ...]

    career_names: tuple[str, ...]


def load_onet_occupation_groups(
) -> tuple[OccupationGroup, ...]:
    """
    Load approved active O*NET occupation mappings.

    Careers that map to the same O*NET external_id belong to the
    same occupation group.
    """

    mappings = (
        CareerExternalMapping.objects
        .select_related(
            "career",
            "dataset__source",
        )
        .filter(
            career__active=True,
            dataset__source__name=(
                ONET_SOURCE_NAME
            ),
            dataset__status=(
                ReferenceDataset.Status.ACTIVE
            ),
            review_status=(
                ReviewStatus.APPROVED
            ),
        )
        .order_by(
            "external_id",
            "career__name",
            "career_id",
        )
    )

    grouped = {}

    for mapping in mappings:
        values = grouped.setdefault(
            mapping.external_id,
            {
                "external_title":
                    mapping.external_title,
                "careers": [],
            },
        )

        values[
            "careers"
        ].append(
            (
                mapping.career_id,
                mapping.career.name,
            )
        )

    groups = []

    for (
        external_id,
        values,
    ) in grouped.items():
        careers = tuple(
            sorted(
                values["careers"],
                key=lambda item: (
                    item[1].casefold(),
                    item[0],
                ),
            )
        )

        groups.append(
            OccupationGroup(
                external_id=external_id,
                external_title=(
                    values[
                        "external_title"
                    ]
                ),
                career_ids=tuple(
                    career_id
                    for career_id, _
                    in careers
                ),
                career_names=tuple(
                    career_name
                    for _, career_name
                    in careers
                ),
            )
        )

    return tuple(
        sorted(
            groups,
            key=lambda group: (
                group.external_id,
                group.external_title.casefold(),
            ),
        )
    )


def build_career_to_group_map(
) -> dict[int, OccupationGroup]:
    """
    Return Career ID -> O*NET OccupationGroup.
    """

    groups = (
        load_onet_occupation_groups()
    )

    mapping = {}

    for group in groups:
        for career_id in group.career_ids:
            if career_id in mapping:
                raise ValueError(
                    "A Career cannot belong to more than "
                    "one active approved O*NET occupation."
                )

            mapping[
                career_id
            ] = group

    return mapping


def find_group_rank(
    *,
    ranked_career_ids: tuple[int, ...],
    target_career_id: int,
    career_to_group: (
        dict[int, OccupationGroup]
        | None
    ) = None,
) -> int | None:
    """
    Return the first rank occupied by any Career belonging to the
    target Career's O*NET occupation group.

    Example:

        target = Software Engineer

        ranked:
        1 DevOps Engineer
        2 Software Engineer

    Exact Career rank:
        2

    O*NET occupation-group rank:
        1
    """

    if target_career_id <= 0:
        raise ValueError(
            "target_career_id must be greater than zero."
        )

    if career_to_group is None:
        career_to_group = (
            build_career_to_group_map()
        )

    target_group = (
        career_to_group.get(
            target_career_id
        )
    )

    if target_group is None:
        return None

    target_group_ids = frozenset(
        target_group.career_ids
    )

    for rank, career_id in enumerate(
        ranked_career_ids,
        start=1,
    ):
        if career_id in target_group_ids:
            return rank

    return None


def theoretical_exact_hit_at_1_ceiling(
) -> float:
    """
    Calculate the exact-Career Hit@1 ceiling for an O*NET-only model.

    For each unique O*NET occupation, an O*NET-only scorer can
    distinguish the occupation but cannot legitimately distinguish
    Careers sharing identical occupation evidence.

    Therefore only one exact Career from each O*NET occupation group
    can deterministically occupy rank 1 for otherwise identical
    evidence.
    """

    groups = (
        load_onet_occupation_groups()
    )

    active_career_count = (
        Career.objects
        .filter(
            active=True
        )
        .count()
    )

    if active_career_count == 0:
        raise ValueError(
            "No active Careers are available."
        )

    return (
        len(groups)
        / active_career_count
    )