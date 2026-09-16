"""
Read-only O*NET API v2 In-Demand technology audit for GradNavi.

Purpose:

1. Load every approved active GradNavi O*NET Career mapping.
2. Reduce the mappings to unique O*NET occupation codes.
3. Call the O*NET API v2 In-Demand Skills endpoint.
4. Compare API In-Demand technologies with GradNavi's local
   O*NET 31.0 evidence.
5. Report coverage, counts, percentages, and mismatches.

This script does not modify database records.
"""

import json
import os
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv

from careers.models import (
    CareerExternalMapping,
    CareerSkillEvidence,
    ReferenceDataset,
    ReviewStatus,
)


ONET_SOURCE_NAME = "O*NET Database"
ONET_SOFTWARE_DOMAIN = "onet_software_skills"

API_BASE_URL = (
    "https://api-v2.onetcenter.org/"
    "online/occupations"
)

REQUEST_DELAY_SECONDS = 0.30
REQUEST_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class ApiTechnology:
    title: str
    percentage: Decimal
    hot_technology: bool | None
    in_demand: bool | None


@dataclass(frozen=True)
class OccupationAudit:
    onet_soc_code: str
    onet_title: str
    career_names: tuple[str, ...]

    api_count: int
    local_in_demand_count: int

    api_min_percentage: Decimal | None
    api_max_percentage: Decimal | None

    missing_locally: tuple[str, ...]
    extra_locally: tuple[str, ...]


def load_api_key() -> str:
    """
    Load the O*NET API key from backend/.env.
    """

    env_path = Path(".env").resolve()

    if not env_path.exists():
        raise RuntimeError(
            f".env was not found at {env_path}"
        )

    load_dotenv(
        dotenv_path=env_path
    )

    api_key = os.getenv(
        "ONET_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "ONET_API_KEY was not found in .env"
        )

    return api_key


def load_onet_career_groups():
    """
    Return approved active O*NET Career mappings grouped by SOC code.
    """

    rows = (
        CareerExternalMapping.objects
        .select_related(
            "career",
            "dataset__source",
        )
        .filter(
            career__active=True,
            dataset__status=(
                ReferenceDataset.Status.ACTIVE
            ),
            dataset__source__name=(
                ONET_SOURCE_NAME
            ),
            review_status=(
                ReviewStatus.APPROVED
            ),
        )
        .order_by(
            "external_id",
            "career__name",
        )
    )

    grouped = {}

    for row in rows:
        group = grouped.setdefault(
            row.external_id,
            {
                "title": row.external_title,
                "careers": [],
            },
        )

        if (
            group["title"]
            != row.external_title
        ):
            raise RuntimeError(
                "Conflicting O*NET titles for "
                f"{row.external_id}"
            )

        group["careers"].append(
            row.career.name
        )

    return grouped


def fetch_in_demand_skills(
    *,
    api_key: str,
    onet_soc_code: str,
) -> tuple[ApiTechnology, ...]:
    """
    Fetch one occupation's In-Demand technologies from O*NET API v2.
    """

    encoded_code = quote(
        onet_soc_code,
        safe=".-",
    )

    url = (
        f"{API_BASE_URL}/"
        f"{encoded_code}/"
        "in_demand_skills"
        "?start=1&end=2000&sort=percentage"
    )

    request = Request(
        url,
        headers={
            "X-API-Key": api_key,
            "Accept": "application/json",
            "User-Agent": "GradNavi/1.0",
        },
    )

    try:
        with urlopen(
            request,
            timeout=(
                REQUEST_TIMEOUT_SECONDS
            ),
        ) as response:
            payload = json.load(
                response
            )

    except HTTPError as error:
        body = (
            error.read()
            .decode(
                "utf-8",
                errors="replace",
            )
        )

        raise RuntimeError(
            "O*NET API HTTP error "
            f"{error.code} for "
            f"{onet_soc_code}: "
            f"{body[:500]}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            "O*NET API connection error "
            f"for {onet_soc_code}: "
            f"{error.reason}"
        ) from error

    items = payload.get(
        "example"
    )

    if not isinstance(
        items,
        list,
    ):
        raise RuntimeError(
            "O*NET API response did not contain "
            f"an example list for {onet_soc_code}"
        )

    technologies = []

    for item in items:
        title = (
            item.get("title")
            or ""
        ).strip()

        percentage_value = (
            item.get("percentage")
        )

        if not title:
            raise RuntimeError(
                "O*NET API returned a blank "
                f"technology title for {onet_soc_code}"
            )

        if percentage_value is None:
            raise RuntimeError(
                "O*NET API returned no percentage for "
                f"{onet_soc_code} | {title}"
            )

        percentage = Decimal(
            str(
                percentage_value
            )
        )

        technologies.append(
            ApiTechnology(
                title=title,
                percentage=percentage,
                hot_technology=(
                    item.get(
                        "hot_technology"
                    )
                ),
                in_demand=(
                    item.get(
                        "in_demand"
                    )
                ),
            )
        )

    return tuple(
        technologies
    )


def load_local_in_demand_titles(
    *,
    onet_soc_code: str,
) -> tuple[str, ...]:
    """
    Return local GradNavi technologies marked In Demand
    for one O*NET occupation code.
    """

    rows = (
        CareerSkillEvidence.objects
        .select_related(
            "career_skill__skill",
            "dataset__source",
        )
        .filter(
            dataset__status=(
                ReferenceDataset.Status.ACTIVE
            ),
            dataset__source__name=(
                ONET_SOURCE_NAME
            ),
            source_domain=(
                ONET_SOFTWARE_DOMAIN
            ),
            external_occupation_id=(
                onet_soc_code
            ),
            in_demand=True,
            not_relevant=False,
        )
        .exclude(
            recommend_suppress=True
        )
        .values_list(
            "career_skill__skill__name",
            flat=True,
        )
        .distinct()
        .order_by(
            "career_skill__skill__name"
        )
    )

    return tuple(
        rows
    )


def run_audit():
    """
    Run the complete read-only O*NET demand audit.
    """

    api_key = load_api_key()

    groups = (
        load_onet_career_groups()
    )

    print(
        "=== O*NET API V2 DEMAND AUDIT ==="
    )

    print(
        "UNIQUE O*NET OCCUPATIONS:",
        len(groups),
    )

    print(
        "ACTIVE CAREER MAPPINGS:",
        sum(
            len(
                info["careers"]
            )
            for info
            in groups.values()
        ),
    )

    print()

    audits = []
    failures = []

    for index, (
        onet_soc_code,
        info,
    ) in enumerate(
        groups.items(),
        start=1,
    ):
        print(
            f"[{index:02}/{len(groups):02}] "
            f"{onet_soc_code} | "
            f"{info['title']}"
        )

        try:
            api_technologies = (
                fetch_in_demand_skills(
                    api_key=api_key,
                    onet_soc_code=(
                        onet_soc_code
                    ),
                )
            )

            local_titles = (
                load_local_in_demand_titles(
                    onet_soc_code=(
                        onet_soc_code
                    )
                )
            )

            api_titles = {
                technology.title
                for technology
                in api_technologies
            }

            local_title_set = set(
                local_titles
            )

            missing_locally = tuple(
                sorted(
                    api_titles
                    - local_title_set,
                    key=str.casefold,
                )
            )

            extra_locally = tuple(
                sorted(
                    local_title_set
                    - api_titles,
                    key=str.casefold,
                )
            )

            percentages = tuple(
                technology.percentage
                for technology
                in api_technologies
            )

            audit = OccupationAudit(
                onet_soc_code=(
                    onet_soc_code
                ),
                onet_title=(
                    info["title"]
                ),
                career_names=tuple(
                    info["careers"]
                ),
                api_count=(
                    len(
                        api_technologies
                    )
                ),
                local_in_demand_count=(
                    len(
                        local_titles
                    )
                ),
                api_min_percentage=(
                    min(percentages)
                    if percentages
                    else None
                ),
                api_max_percentage=(
                    max(percentages)
                    if percentages
                    else None
                ),
                missing_locally=(
                    missing_locally
                ),
                extra_locally=(
                    extra_locally
                ),
            )

            audits.append(
                audit
            )

            print(
                "    API:",
                audit.api_count,
                "| LOCAL:",
                audit.local_in_demand_count,
                "| MIN %:",
                audit.api_min_percentage,
                "| MAX %:",
                audit.api_max_percentage,
                "| MISSING LOCAL:",
                len(
                    audit.missing_locally
                ),
                "| EXTRA LOCAL:",
                len(
                    audit.extra_locally
                ),
            )

        except Exception as error:
            failures.append(
                (
                    onet_soc_code,
                    str(error),
                )
            )

            print(
                "    FAILED:",
                error,
            )

        if index < len(groups):
            time.sleep(
                REQUEST_DELAY_SECONDS
            )

    print()
    print(
        "=== AUDIT SUMMARY ==="
    )

    print(
        "REQUESTED OCCUPATIONS:",
        len(groups),
    )

    print(
        "SUCCESSFUL:",
        len(audits),
    )

    print(
        "FAILED:",
        len(failures),
    )

    print(
        "TOTAL API TECHNOLOGIES:",
        sum(
            audit.api_count
            for audit
            in audits
        ),
    )

    print(
        "TOTAL LOCAL IN-DEMAND:",
        sum(
            audit.local_in_demand_count
            for audit
            in audits
        ),
    )

    mismatched = tuple(
        audit
        for audit
        in audits
        if (
            audit.missing_locally
            or audit.extra_locally
            or (
                audit.api_count
                !=
                audit.local_in_demand_count
            )
        )
    )

    print(
        "OCCUPATIONS WITH MISMATCHES:",
        len(mismatched),
    )

    print()
    print(
        "=== PERCENTAGE RANGE ==="
    )

    all_minimums = [
        audit.api_min_percentage
        for audit
        in audits
        if (
            audit.api_min_percentage
            is not None
        )
    ]

    all_maximums = [
        audit.api_max_percentage
        for audit
        in audits
        if (
            audit.api_max_percentage
            is not None
        )
    ]

    print(
        "LOWEST RETURNED PERCENTAGE:",
        (
            min(all_minimums)
            if all_minimums
            else None
        ),
    )

    print(
        "HIGHEST RETURNED PERCENTAGE:",
        (
            max(all_maximums)
            if all_maximums
            else None
        ),
    )

    if mismatched:
        print()
        print(
            "=== MISMATCH DETAILS ==="
        )

        for audit in mismatched:
            print()
            print(
                audit.onet_soc_code,
                "|",
                audit.onet_title,
            )

            print(
                "CAREERS:",
                ", ".join(
                    audit.career_names
                ),
            )

            print(
                "API COUNT:",
                audit.api_count,
            )

            print(
                "LOCAL COUNT:",
                audit.local_in_demand_count,
            )

            if audit.missing_locally:
                print(
                    "MISSING LOCALLY:"
                )

                for title in (
                    audit.missing_locally
                ):
                    print(
                        "  +",
                        title,
                    )

            if audit.extra_locally:
                print(
                    "EXTRA LOCALLY:"
                )

                for title in (
                    audit.extra_locally
                ):
                    print(
                        "  -",
                        title,
                    )

    if failures:
        print()
        print(
            "=== API FAILURES ==="
        )

        for (
            onet_soc_code,
            message,
        ) in failures:
            print(
                onet_soc_code,
                "|",
                message,
            )


run_audit()
