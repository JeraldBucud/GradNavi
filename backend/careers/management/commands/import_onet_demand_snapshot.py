"""
Import a frozen O*NET API v2 In-Demand percentage snapshot.

This command enriches existing GradNavi O*NET software evidence
with source-native occupation demand percentages.

The base Dataset 1.0 importer stays separate.

Usage:

    python manage.py import_onet_demand_snapshot \
        --snapshot-date 2026-09-16 \
        --dry-run

    python manage.py import_onet_demand_snapshot \
        --snapshot-date 2026-09-16

Safety:

- Validates the snapshot manifest.
- Validates SHA-256 hashes.
- Confirms the snapshot O*NET version matches the active
  GradNavi O*NET dataset.
- Confirms occupation and technology keys match local evidence.
- Confirms percentage values stay within 0 to 100.
- Confirms only In-Demand O*NET software evidence receives
  percentages.
- Supports transaction rollback through --dry-run.
"""

import csv
import hashlib
import json

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db import transaction

from careers.models import (
    CareerExternalMapping,
    CareerSkillEvidence,
    ReferenceDataset,
    ReviewStatus,
)


ONET_SOURCE_NAME = "O*NET Database"
ONET_SOFTWARE_DOMAIN = "onet_software_skills"

EXPECTED_SOURCE = (
    "O*NET Web Services API v2"
)

EXPECTED_SCHEMA_VERSION = 1

PERCENTAGE_MINIMUM = Decimal("0")
PERCENTAGE_MAXIMUM = Decimal("100")
PERCENTAGE_QUANTUM = Decimal("0.01")


class Command(BaseCommand):
    """
    Import one immutable O*NET API v2 demand snapshot.
    """

    help = (
        "Import O*NET API v2 In-Demand technology percentages "
        "from a validated local snapshot."
    )

    def add_arguments(
        self,
        parser,
    ):
        parser.add_argument(
            "--snapshot-date",
            required=True,
            help=(
                "Snapshot directory date in YYYY-MM-DD format, "
                "for example 2026-09-16."
            ),
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Validate and perform the import inside a "
                "transaction, then roll back all changes."
            ),
        )

    def sha256_file(
        self,
        path: Path,
    ) -> str:
        """
        Return the SHA-256 checksum for one file.
        """

        digest = hashlib.sha256()

        with path.open("rb") as handle:
            for chunk in iter(
                lambda: handle.read(
                    1024 * 1024
                ),
                b"",
            ):
                digest.update(
                    chunk
                )

        return digest.hexdigest()

    def parse_percentage(
        self,
        value,
        *,
        occupation_id: str,
        technology_title: str,
    ) -> Decimal:
        """
        Parse one source percentage onto GradNavi's 0-100 scale.
        """

        try:
            percentage = Decimal(
                str(
                    value
                ).strip()
            )

        except (
            InvalidOperation,
            AttributeError,
        ) as error:
            raise CommandError(
                "Invalid percentage for "
                f"{occupation_id} | "
                f"{technology_title}: "
                f"{value!r}"
            ) from error

        if not (
            PERCENTAGE_MINIMUM
            <= percentage
            <= PERCENTAGE_MAXIMUM
        ):
            raise CommandError(
                "Percentage outside 0 to 100 for "
                f"{occupation_id} | "
                f"{technology_title}: "
                f"{percentage}"
            )

        return percentage.quantize(
            PERCENTAGE_QUANTUM
        )

    def parse_boolean(
        self,
        value,
        *,
        field_name: str,
        occupation_id: str,
        technology_title: str,
    ) -> bool:
        """
        Parse a normalized CSV boolean value.
        """

        normalized = (
            str(
                value
            )
            .strip()
            .casefold()
        )

        if normalized == "true":
            return True

        if normalized == "false":
            return False

        raise CommandError(
            f"Invalid {field_name} value for "
            f"{occupation_id} | "
            f"{technology_title}: "
            f"{value!r}"
        )

    def load_active_onet_dataset(
        self,
    ):
        """
        Return the single active O*NET reference dataset.
        """

        datasets = tuple(
            ReferenceDataset.objects
            .select_related(
                "source",
            )
            .filter(
                source__name=(
                    ONET_SOURCE_NAME
                ),
                status=(
                    ReferenceDataset
                    .Status
                    .ACTIVE
                ),
            )
        )

        if len(datasets) != 1:
            raise CommandError(
                "Expected exactly one active O*NET dataset. "
                f"Found {len(datasets)}."
            )

        return datasets[0]

    def load_career_mapping_count(
        self,
    ) -> int:
        """
        Count approved active GradNavi O*NET Career mappings.
        """

        return (
            CareerExternalMapping.objects
            .filter(
                career__active=True,
                dataset__status=(
                    ReferenceDataset
                    .Status
                    .ACTIVE
                ),
                dataset__source__name=(
                    ONET_SOURCE_NAME
                ),
                review_status=(
                    ReviewStatus.APPROVED
                ),
            )
            .count()
        )

    def handle(
        self,
        *args,
        **options,
    ):
        snapshot_date = (
            options[
                "snapshot_date"
            ]
            .strip()
        )

        dry_run = bool(
            options["dry_run"]
        )

        repo_root = (
            Path(__file__)
            .resolve()
            .parents[4]
        )

        snapshot_directory = (
            repo_root
            / "data"
            / "reference"
            / "snapshots"
            / "onet_api_v2_in_demand"
            / snapshot_date
        )

        manifest_path = (
            snapshot_directory
            / "snapshot_manifest.json"
        )

        raw_path = (
            snapshot_directory
            / "onet_api_v2_in_demand_raw.json"
        )

        csv_path = (
            snapshot_directory
            / "onet_api_v2_in_demand_normalized.csv"
        )

        self.stdout.write(
            "=" * 100
        )

        self.stdout.write(
            "GRADNAVI O*NET DEMAND SNAPSHOT IMPORT"
        )

        self.stdout.write(
            "=" * 100
        )

        self.stdout.write("")

        self.stdout.write(
            f"Snapshot date: {snapshot_date}"
        )

        self.stdout.write(
            f"Snapshot path: {snapshot_directory}"
        )

        self.stdout.write("")

        for path in (
            manifest_path,
            raw_path,
            csv_path,
        ):
            if not path.exists():
                raise CommandError(
                    "Required snapshot file is missing: "
                    f"{path}"
                )

        self.stdout.write(
            "1. SNAPSHOT MANIFEST"
        )

        self.stdout.write(
            "-" * 100
        )

        manifest = json.loads(
            manifest_path.read_text(
                encoding="utf-8"
            )
        )

        if (
            manifest.get(
                "schema_version"
            )
            != EXPECTED_SCHEMA_VERSION
        ):
            raise CommandError(
                "Unsupported snapshot schema version: "
                f"{manifest.get('schema_version')}"
            )

        if (
            manifest.get("source")
            != EXPECTED_SOURCE
        ):
            raise CommandError(
                "Unexpected snapshot source: "
                f"{manifest.get('source')!r}"
            )

        if (
            manifest.get(
                "snapshot_date"
            )
            != snapshot_date
        ):
            raise CommandError(
                "Snapshot directory date does not match "
                "manifest snapshot_date."
            )

        if (
            manifest.get(
                "validation",
                {},
            ).get(
                "api_key_written_to_snapshot"
            )
            is not False
        ):
            raise CommandError(
                "Snapshot manifest does not confirm "
                "API-key exclusion."
            )

        if (
            manifest.get(
                "validation",
                {},
            ).get(
                "api_local_mismatch_count"
            )
            != 0
        ):
            raise CommandError(
                "Snapshot was not frozen with zero "
                "API/local mismatches."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Manifest schema/source"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] API key excluded"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Snapshot mismatch count: 0"
            )
        )

        self.stdout.write("")
        self.stdout.write(
            "2. SNAPSHOT FILE HASHES"
        )

        self.stdout.write(
            "-" * 100
        )

        expected_raw_hash = (
            manifest[
                "files"
            ][
                raw_path.name
            ][
                "sha256"
            ]
        )

        expected_csv_hash = (
            manifest[
                "files"
            ][
                csv_path.name
            ][
                "sha256"
            ]
        )

        actual_raw_hash = (
            self.sha256_file(
                raw_path
            )
        )

        actual_csv_hash = (
            self.sha256_file(
                csv_path
            )
        )

        if (
            actual_raw_hash
            != expected_raw_hash
        ):
            raise CommandError(
                "Raw JSON SHA-256 mismatch."
            )

        if (
            actual_csv_hash
            != expected_csv_hash
        ):
            raise CommandError(
                "Normalized CSV SHA-256 mismatch."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Raw JSON SHA-256"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Normalized CSV SHA-256"
            )
        )

        self.stdout.write("")
        self.stdout.write(
            "3. O*NET DATASET VERSION"
        )

        self.stdout.write(
            "-" * 100
        )

        active_dataset = (
            self.load_active_onet_dataset()
        )

        snapshot_version = (
            str(
                manifest.get(
                    "local_onet_dataset_version"
                )
            )
        )

        if (
            active_dataset.version
            != snapshot_version
        ):
            raise CommandError(
                "Snapshot O*NET version does not match "
                "the active GradNavi O*NET dataset. "
                f"Snapshot={snapshot_version}, "
                f"Database={active_dataset.version}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] O*NET version: "
                f"{active_dataset.version}"
            )
        )

        career_mapping_count = (
            self.load_career_mapping_count()
        )

        if (
            career_mapping_count
            != manifest.get(
                "career_mapping_count"
            )
        ):
            raise CommandError(
                "Active O*NET Career mapping count "
                "does not match snapshot manifest."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Career mappings: "
                f"{career_mapping_count}"
            )
        )

        self.stdout.write("")
        self.stdout.write(
            "4. NORMALIZED SNAPSHOT DATA"
        )

        self.stdout.write(
            "-" * 100
        )

        with csv_path.open(
            encoding="utf-8-sig",
            newline="",
        ) as handle:
            reader = csv.DictReader(
                handle
            )

            expected_fields = {
                "onet_soc_code",
                "onet_title",
                "gradnavi_careers",
                "api_position",
                "technology_title",
                "percentage",
                "hot_technology",
                "in_demand",
                "source_url",
            }

            actual_fields = set(
                reader.fieldnames
                or ()
            )

            if (
                actual_fields
                != expected_fields
            ):
                raise CommandError(
                    "Unexpected normalized snapshot "
                    "CSV columns. "
                    f"Expected={sorted(expected_fields)}, "
                    f"Actual={sorted(actual_fields)}"
                )

            rows = list(
                reader
            )

        if (
            len(rows)
            != manifest.get(
                "technology_row_count"
            )
        ):
            raise CommandError(
                "Normalized snapshot row count "
                "does not match manifest."
            )

        snapshot_values = {}

        occupation_ids = set()

        for row in rows:
            occupation_id = (
                row[
                    "onet_soc_code"
                ]
                .strip()
            )

            technology_title = (
                row[
                    "technology_title"
                ]
                .strip()
            )

            if not occupation_id:
                raise CommandError(
                    "Snapshot contains a blank "
                    "O*NET occupation code."
                )

            if not technology_title:
                raise CommandError(
                    "Snapshot contains a blank "
                    "technology title."
                )

            percentage = (
                self.parse_percentage(
                    row["percentage"],
                    occupation_id=(
                        occupation_id
                    ),
                    technology_title=(
                        technology_title
                    ),
                )
            )

            in_demand = (
                self.parse_boolean(
                    row["in_demand"],
                    field_name=(
                        "in_demand"
                    ),
                    occupation_id=(
                        occupation_id
                    ),
                    technology_title=(
                        technology_title
                    ),
                )
            )

            if not in_demand:
                raise CommandError(
                    "The In-Demand snapshot contains "
                    "a row with in_demand=False: "
                    f"{occupation_id} | "
                    f"{technology_title}"
                )

            key = (
                occupation_id,
                technology_title,
            )

            if key in snapshot_values:
                raise CommandError(
                    "Duplicate occupation/technology "
                    "snapshot key: "
                    f"{occupation_id} | "
                    f"{technology_title}"
                )

            snapshot_values[
                key
            ] = percentage

            occupation_ids.add(
                occupation_id
            )

        if (
            len(
                occupation_ids
            )
            != manifest.get(
                "occupation_count"
            )
            - manifest.get(
                "zero_result_occupation_count"
            )
        ):
            raise CommandError(
                "Occupation count represented by "
                "technology rows does not match "
                "snapshot manifest coverage."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Snapshot technology rows: "
                f"{len(rows)}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Unique occupation/technology keys: "
                f"{len(snapshot_values)}"
            )
        )

        self.stdout.write("")
        self.stdout.write(
            "5. LOCAL EVIDENCE MATCHING"
        )

        self.stdout.write(
            "-" * 100
        )

        evidence_rows = tuple(
            CareerSkillEvidence.objects
            .select_related(
                "career_skill__career",
                "career_skill__skill",
                "dataset__source",
            )
            .filter(
                career_skill__career__active=True,
                career_skill__review_status=(
                    ReviewStatus.APPROVED
                ),
                dataset=(
                    active_dataset
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
            .order_by(
                "external_occupation_id",
                "career_skill__skill__name",
                "career_skill__career__name",
                "id",
            )
        )

        evidence_by_key = (
            defaultdict(
                list
            )
        )

        for evidence in evidence_rows:
            key = (
                evidence.external_occupation_id,
                evidence.career_skill.skill.name,
            )

            evidence_by_key[
                key
            ].append(
                evidence
            )

        local_keys = set(
            evidence_by_key
        )

        snapshot_keys = set(
            snapshot_values
        )

        missing_locally = (
            snapshot_keys
            - local_keys
        )

        extra_locally = (
            local_keys
            - snapshot_keys
        )

        if missing_locally:
            examples = sorted(
                missing_locally
            )[:10]

            raise CommandError(
                "Snapshot contains occupation/technology "
                "keys missing from local evidence. "
                f"Examples: {examples}"
            )

        if extra_locally:
            examples = sorted(
                extra_locally
            )[:10]

            raise CommandError(
                "Local In-Demand evidence contains keys "
                "missing from the snapshot. "
                f"Examples: {examples}"
            )

        matched_evidence_count = sum(
            len(
                evidence_by_key[
                    key
                ]
            )
            for key
            in snapshot_keys
        )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Snapshot keys match "
                "local In-Demand evidence"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Unique source keys: "
                f"{len(snapshot_keys)}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Career-level evidence rows: "
                f"{matched_evidence_count}"
            )
        )

        self.stdout.write("")
        self.stdout.write(
            "6. PERCENTAGE IMPORT"
        )

        self.stdout.write(
            "-" * 100
        )

        updated_count = 0
        unchanged_count = 0

        with transaction.atomic():
            to_update = []

            for (
                key,
                percentage,
            ) in snapshot_values.items():
                for evidence in (
                    evidence_by_key[
                        key
                    ]
                ):
                    if (
                        evidence
                        .in_demand_percentage
                        == percentage
                    ):
                        unchanged_count += 1
                        continue

                    evidence.in_demand_percentage = (
                        percentage
                    )

                    to_update.append(
                        evidence
                    )

            if to_update:
                CareerSkillEvidence.objects.bulk_update(
                    to_update,
                    [
                        "in_demand_percentage",
                    ],
                )

            updated_count = len(
                to_update
            )

            populated_count = (
                CareerSkillEvidence.objects
                .filter(
                    career_skill__career__active=True,
                    dataset=(
                        active_dataset
                    ),
                    source_domain=(
                        ONET_SOFTWARE_DOMAIN
                    ),
                    in_demand=True,
                    in_demand_percentage__isnull=False,
                    not_relevant=False,
                )
                .exclude(
                    recommend_suppress=True
                )
                .count()
            )

            if (
                populated_count
                != matched_evidence_count
            ):
                raise CommandError(
                    "Final populated percentage count "
                    "does not match matched evidence count. "
                    f"Expected={matched_evidence_count}, "
                    f"Actual={populated_count}"
                )

            non_demand_populated = (
                CareerSkillEvidence.objects
                .filter(
                    dataset=(
                        active_dataset
                    ),
                    source_domain=(
                        ONET_SOFTWARE_DOMAIN
                    ),
                    in_demand=False,
                    in_demand_percentage__isnull=False,
                )
                .count()
            )

            if non_demand_populated != 0:
                raise CommandError(
                    "Non-In-Demand O*NET software evidence "
                    "received a percentage."
                )

            non_software_populated = (
                CareerSkillEvidence.objects
                .filter(
                    dataset=(
                        active_dataset
                    ),
                    in_demand_percentage__isnull=False,
                )
                .exclude(
                    source_domain=(
                        ONET_SOFTWARE_DOMAIN
                    )
                )
                .count()
            )

            if non_software_populated != 0:
                raise CommandError(
                    "Non-software O*NET evidence received "
                    "an In-Demand percentage."
                )

            self.stdout.write(
                self.style.SUCCESS(
                    "[PASS] Populated In-Demand evidence: "
                    f"{populated_count}"
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "[PASS] Non-In-Demand percentages: 0"
                )
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "[PASS] Non-software percentages: 0"
                )
            )

            if dry_run:
                transaction.set_rollback(
                    True
                )

        self.stdout.write("")
        self.stdout.write(
            "7. IMPORT SUMMARY"
        )

        self.stdout.write(
            "-" * 100
        )

        self.stdout.write(
            f"Snapshot source rows: {len(snapshot_values)}"
        )

        self.stdout.write(
            "Career-level evidence rows: "
            f"{matched_evidence_count}"
        )

        self.stdout.write(
            f"Evidence rows updated: {updated_count}"
        )

        self.stdout.write(
            f"Evidence rows unchanged: {unchanged_count}"
        )

        self.stdout.write("")

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    "DRY RUN PASSED: all database "
                    "changes were rolled back."
                )
            )

        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "O*NET DEMAND SNAPSHOT IMPORT: PASSED"
                )
            )
