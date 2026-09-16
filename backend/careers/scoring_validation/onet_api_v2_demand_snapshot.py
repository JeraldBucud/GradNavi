"""
Freeze a validated O*NET API v2 In-Demand technology snapshot.

Outputs:

1. Raw JSON snapshot.
2. Normalized CSV snapshot.
3. Snapshot manifest with provenance and SHA-256 hashes.

Safety:

- The API key is loaded from backend/.env.
- The API key is never written to snapshot files.
- API data is validated against GradNavi's existing approved
  O*NET In-Demand technology evidence before files are written.
- Any API/local mismatch aborts snapshot creation.
"""

import csv
import hashlib
import json
import os
import time

from collections import defaultdict
from datetime import datetime, timezone
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

SNAPSHOT_ROOT = Path(
    "../data/reference/snapshots/"
    "onet_api_v2_in_demand"
)


def sha256_file(path: Path) -> str:
    """
    Return the SHA-256 checksum for one file.
    """

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def load_api_key() -> str:
    """
    Load O*NET API credentials without printing them.
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


def load_active_onet_dataset():
    """
    Return GradNavi's active local O*NET dataset.
    """

    datasets = tuple(
        ReferenceDataset.objects
        .select_related(
            "source",
        )
        .filter(
            source__name=ONET_SOURCE_NAME,
            status=(
                ReferenceDataset.Status.ACTIVE
            ),
        )
    )

    if len(datasets) != 1:
        raise RuntimeError(
            "Expected exactly one active O*NET dataset. "
            f"Found {len(datasets)}."
        )

    return datasets[0]


def load_onet_career_groups():
    """
    Return approved GradNavi O*NET mappings grouped by SOC code.
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


def load_local_in_demand_titles():
    """
    Return local In-Demand technology titles by O*NET SOC code.
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
            in_demand=True,
            not_relevant=False,
        )
        .exclude(
            recommend_suppress=True
        )
        .values_list(
            "external_occupation_id",
            "career_skill__skill__name",
        )
        .distinct()
        .order_by(
            "external_occupation_id",
            "career_skill__skill__name",
        )
    )

    grouped = defaultdict(
        set
    )

    for (
        occupation_id,
        skill_name,
    ) in rows:
        grouped[
            occupation_id
        ].add(
            skill_name
        )

    return grouped


def fetch_occupation(
    *,
    api_key: str,
    onet_soc_code: str,
):
    """
    Fetch one raw O*NET API v2 In-Demand Skills payload.
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
            status = response.status
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

    if status != 200:
        raise RuntimeError(
            "Unexpected O*NET API HTTP status "
            f"{status} for {onet_soc_code}."
        )

    items = payload.get(
        "example"
    )

    if not isinstance(
        items,
        list,
    ):
        raise RuntimeError(
            "O*NET API response did not contain "
            f"an example list for {onet_soc_code}."
        )

    return (
        url,
        payload,
        items,
    )


def validate_item(
    *,
    onet_soc_code: str,
    item: dict,
):
    """
    Validate one normalized API technology row.
    """

    title = (
        item.get("title")
        or ""
    ).strip()

    if not title:
        raise RuntimeError(
            "Blank technology title for "
            f"{onet_soc_code}."
        )

    percentage = item.get(
        "percentage"
    )

    if percentage is None:
        raise RuntimeError(
            "Missing percentage for "
            f"{onet_soc_code} | {title}"
        )

    numeric_percentage = float(
        percentage
    )

    if not (
        0
        <= numeric_percentage
        <= 100
    ):
        raise RuntimeError(
            "Percentage outside 0 to 100 for "
            f"{onet_soc_code} | {title}: "
            f"{percentage}"
        )

    in_demand = item.get(
        "in_demand"
    )

    if in_demand is not True:
        raise RuntimeError(
            "In-Demand endpoint returned a row "
            "without in_demand=True: "
            f"{onet_soc_code} | {title}"
        )


def write_json(
    *,
    path: Path,
    payload: dict,
):
    """
    Write deterministic UTF-8 JSON.
    """

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def run_snapshot():
    """
    Fetch, validate, and freeze the O*NET API v2 snapshot.
    """

    api_key = load_api_key()

    active_dataset = (
        load_active_onet_dataset()
    )

    groups = (
        load_onet_career_groups()
    )

    local_titles = (
        load_local_in_demand_titles()
    )

    retrieved_local = (
        datetime.now()
        .astimezone()
    )

    retrieved_utc = (
        datetime.now(
            timezone.utc
        )
    )

    snapshot_date = (
        retrieved_local
        .date()
        .isoformat()
    )

    output_directory = (
        SNAPSHOT_ROOT
        / snapshot_date
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_path = (
        output_directory
        / "onet_api_v2_in_demand_raw.json"
    )

    csv_path = (
        output_directory
        / "onet_api_v2_in_demand_normalized.csv"
    )

    manifest_path = (
        output_directory
        / "snapshot_manifest.json"
    )

    existing_outputs = [
        path
        for path in (
            raw_path,
            csv_path,
            manifest_path,
        )
        if path.exists()
    ]

    if existing_outputs:
        raise RuntimeError(
            "Snapshot files already exist for "
            f"{snapshot_date}. "
            "Existing snapshots are immutable. "
            "Do not overwrite them."
        )

    print(
        "=== FREEZE O*NET API V2 SNAPSHOT ==="
    )

    print(
        "LOCAL O*NET VERSION:",
        active_dataset.version,
    )

    print(
        "OCCUPATIONS:",
        len(groups),
    )

    print(
        "CAREER MAPPINGS:",
        sum(
            len(
                info["careers"]
            )
            for info
            in groups.values()
        ),
    )

    print(
        "SNAPSHOT DATE:",
        snapshot_date,
    )

    print()

    raw_occupations = []
    normalized_rows = []

    mismatch_count = 0

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

        (
            source_url,
            payload,
            items,
        ) = fetch_occupation(
            api_key=api_key,
            onet_soc_code=(
                onet_soc_code
            ),
        )

        api_titles = set()

        for position, item in enumerate(
            items,
            start=1,
        ):
            validate_item(
                onet_soc_code=(
                    onet_soc_code
                ),
                item=item,
            )

            title = (
                item["title"]
                .strip()
            )

            api_titles.add(
                title
            )

            normalized_rows.append(
                {
                    "onet_soc_code":
                        onet_soc_code,

                    "onet_title":
                        info["title"],

                    "gradnavi_careers":
                        "; ".join(
                            info["careers"]
                        ),

                    "api_position":
                        position,

                    "technology_title":
                        title,

                    "percentage":
                        item[
                            "percentage"
                        ],

                    "hot_technology":
                        item.get(
                            "hot_technology"
                        ),

                    "in_demand":
                        item.get(
                            "in_demand"
                        ),

                    "source_url":
                        source_url,
                }
            )

        expected_local = set(
            local_titles.get(
                onet_soc_code,
                set(),
            )
        )

        missing_locally = (
            api_titles
            - expected_local
        )

        extra_locally = (
            expected_local
            - api_titles
        )

        if (
            missing_locally
            or extra_locally
        ):
            mismatch_count += 1

            print(
                "    MISMATCH"
            )

            print(
                "    Missing locally:",
                sorted(
                    missing_locally,
                    key=str.casefold,
                ),
            )

            print(
                "    Extra locally:",
                sorted(
                    extra_locally,
                    key=str.casefold,
                ),
            )

        else:
            print(
                "    VALIDATED:",
                len(items),
                "technology rows",
            )

        raw_occupations.append(
            {
                "onet_soc_code":
                    onet_soc_code,

                "onet_title":
                    info["title"],

                "gradnavi_careers":
                    tuple(
                        info["careers"]
                    ),

                "source_url":
                    source_url,

                "response":
                    payload,
            }
        )

        if index < len(groups):
            time.sleep(
                REQUEST_DELAY_SECONDS
            )

    if mismatch_count:
        raise RuntimeError(
            "Snapshot aborted. "
            f"{mismatch_count} occupation(s) "
            "did not match local evidence."
        )

    print()
    print(
        "ALL API OCCUPATIONS MATCH LOCAL DATA."
    )

    raw_snapshot = {
        "schema_version": 1,

        "source": (
            "O*NET Web Services API v2"
        ),

        "local_reference_source": (
            ONET_SOURCE_NAME
        ),

        "local_onet_dataset_version": (
            active_dataset.version
        ),

        "retrieved_at_utc": (
            retrieved_utc
            .isoformat()
        ),

        "retrieved_at_local": (
            retrieved_local
            .isoformat()
        ),

        "occupation_count": (
            len(groups)
        ),

        "career_mapping_count": (
            sum(
                len(
                    info["careers"]
                )
                for info
                in groups.values()
            )
        ),

        "technology_row_count": (
            len(
                normalized_rows
            )
        ),

        "occupations": (
            raw_occupations
        ),
    }

    write_json(
        path=raw_path,
        payload=raw_snapshot,
    )

    csv_fieldnames = [
        "onet_soc_code",
        "onet_title",
        "gradnavi_careers",
        "api_position",
        "technology_title",
        "percentage",
        "hot_technology",
        "in_demand",
        "source_url",
    ]

    with csv_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                csv_fieldnames
            ),
        )

        writer.writeheader()

        writer.writerows(
            normalized_rows
        )

    raw_sha256 = (
        sha256_file(
            raw_path
        )
    )

    csv_sha256 = (
        sha256_file(
            csv_path
        )
    )

    percentages = [
        float(
            row["percentage"]
        )
        for row
        in normalized_rows
    ]

    zero_result_occupations = [
        occupation
        for occupation
        in raw_occupations
        if not (
            occupation[
                "response"
            ].get(
                "example"
            )
        )
    ]

    manifest = {
        "schema_version": 1,

        "snapshot_date": (
            snapshot_date
        ),

        "source": (
            "O*NET Web Services API v2"
        ),

        "api_base_url": (
            API_BASE_URL
        ),

        "local_onet_dataset_version": (
            active_dataset.version
        ),

        "retrieved_at_utc": (
            retrieved_utc
            .isoformat()
        ),

        "retrieved_at_local": (
            retrieved_local
            .isoformat()
        ),

        "occupation_count": (
            len(groups)
        ),

        "career_mapping_count": (
            sum(
                len(
                    info["careers"]
                )
                for info
                in groups.values()
            )
        ),

        "technology_row_count": (
            len(
                normalized_rows
            )
        ),

        "zero_result_occupation_count": (
            len(
                zero_result_occupations
            )
        ),

        "zero_result_occupations": [
            {
                "onet_soc_code":
                    occupation[
                        "onet_soc_code"
                    ],

                "onet_title":
                    occupation[
                        "onet_title"
                    ],
            }
            for occupation
            in zero_result_occupations
        ],

        "minimum_percentage": (
            min(
                percentages
            )
            if percentages
            else None
        ),

        "maximum_percentage": (
            max(
                percentages
            )
            if percentages
            else None
        ),

        "validation": {
            "api_local_mismatch_count":
                mismatch_count,

            "api_key_written_to_snapshot":
                False,
        },

        "files": {
            raw_path.name: {
                "sha256":
                    raw_sha256,
            },

            csv_path.name: {
                "sha256":
                    csv_sha256,
            },
        },
    }

    write_json(
        path=manifest_path,
        payload=manifest,
    )

    print()
    print(
        "=== SNAPSHOT CREATED ==="
    )

    print(
        "DIRECTORY:",
        output_directory.resolve(),
    )

    print(
        "RAW JSON:",
        raw_path.name,
    )

    print(
        "NORMALIZED CSV:",
        csv_path.name,
    )

    print(
        "MANIFEST:",
        manifest_path.name,
    )

    print()
    print(
        "OCCUPATIONS:",
        len(groups),
    )

    print(
        "TECHNOLOGY ROWS:",
        len(
            normalized_rows
        ),
    )

    print(
        "ZERO-RESULT OCCUPATIONS:",
        len(
            zero_result_occupations
        ),
    )

    print(
        "MINIMUM PERCENTAGE:",
        (
            min(
                percentages
            )
            if percentages
            else None
        ),
    )

    print(
        "MAXIMUM PERCENTAGE:",
        (
            max(
                percentages
            )
            if percentages
            else None
        ),
    )

    print()
    print(
        "RAW SHA256:",
        raw_sha256,
    )

    print(
        "CSV SHA256:",
        csv_sha256,
    )

    print()
    print(
        "SNAPSHOT FREEZE: PASSED"
    )


run_snapshot()
