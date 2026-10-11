"""
Shared evidence eligibility policy for GradNavi Career analysis.

WBS 5.3 Career Recommendation competency scoring and
WBS 5.5 Career Readiness must use the same definition
of a core O*NET competency.

The minimum normalized O*NET Importance threshold was
selected after a read-only audit across all 36 active
GradNavi Careers.

A value of 50.00 keeps meaningful occupational evidence
while excluding low-relevance descriptors from competency
and readiness calculations.
"""

from decimal import Decimal


CORE_COMPETENCY_MINIMUM_IMPORTANCE = Decimal(
    "50.00"
)


def meets_core_competency_importance(
    importance: Decimal | None,
) -> bool:
    """
    Return True when an O*NET Importance value qualifies
    as core competency evidence.
    """

    return (
        importance is not None
        and importance
        >= CORE_COMPETENCY_MINIMUM_IMPORTANCE
    )
