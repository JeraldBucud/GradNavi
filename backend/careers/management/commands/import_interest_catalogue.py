import csv
from collections import Counter, defaultdict
from pathlib import Path

from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db import transaction

from careers.models import (
    Career,
    CareerInterest,
)
from profiles.models import Interest


class Command(BaseCommand):
    """
    Import the reviewed GradNavi detailed Interest catalogue V1.

    The import is:
    - version controlled
    - transactional
    - repeatable
    - safe for existing Interest records
    - dry-run capable
    """

    help = (
        "Import GradNavi detailed Interest catalogue V1 "
        "and reviewed CareerInterest mappings."
    )

    EXPECTED_CAREERS = 36
    EXPECTED_INTERESTS_PER_CAREER = 10
    EXPECTED_TOTAL_MAPPINGS = 360

    EXPECTED_WEIGHT_DISTRIBUTION = {
        5: 3,
        4: 4,
        3: 3,
    }

    EXPECTED_WEIGHT_TOTAL = 40

    def add_arguments(
        self,
        parser,
    ):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Run the complete import and validation "
                "inside a transaction, then roll back "
                "all database changes."
            ),
        )

    def handle(
        self,
        *args,
        **options,
    ):
        dry_run = options[
            "dry_run"
        ]

        repo_root = (
            Path(__file__)
            .resolve()
            .parents[4]
        )

        data_dir = (
            repo_root
            / "data"
            / "reference"
            / "gradnavi_interests"
            / "v1"
        )

        interest_path = (
            data_dir
            / "interest_catalogue.csv"
        )

        mapping_path = (
            data_dir
            / "career_interest_mappings.csv"
        )

        if not interest_path.exists():
            raise CommandError(
                "Missing Interest catalogue: "
                f"{interest_path}"
            )

        if not mapping_path.exists():
            raise CommandError(
                "Missing CareerInterest mappings: "
                f"{mapping_path}"
            )

        interest_rows = self.load_csv(
            interest_path
        )

        mapping_rows = self.load_csv(
            mapping_path
        )

        self.stdout.write(
            "=" * 100
        )

        self.stdout.write(
            "GRADNAVI INTEREST CATALOGUE V1 IMPORT"
        )

        self.stdout.write(
            "=" * 100
        )

        self.stdout.write(
            ""
        )

        self.validate_source_data(
            interest_rows,
            mapping_rows,
        )

        before = (
            self.database_snapshot()
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            "DATABASE BEFORE IMPORT"
        )

        self.stdout.write(
            "-" * 100
        )

        self.print_snapshot(
            before
        )

        if dry_run:
            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN ENABLED. "
                    "ALL DATABASE CHANGES WILL "
                    "BE ROLLED BACK."
                )
            )

        with transaction.atomic():
            interest_stats = (
                self.import_interests(
                    interest_rows
                )
            )

            mapping_stats = (
                self.import_mappings(
                    mapping_rows
                )
            )

            self.validate_database_state(
                interest_rows,
                mapping_rows,
            )

            after_inside = (
                self.database_snapshot()
            )

            self.stdout.write(
                ""
            )

            self.stdout.write(
                "IMPORT RESULT"
            )

            self.stdout.write(
                "-" * 100
            )

            self.stdout.write(
                "INTERESTS CREATED: "
                f"{interest_stats['created']}"
            )

            self.stdout.write(
                "INTERESTS REUSED: "
                f"{interest_stats['reused']}"
            )

            self.stdout.write(
                "INTERESTS UPDATED: "
                f"{interest_stats['updated']}"
            )

            self.stdout.write(
                "MAPPINGS CREATED: "
                f"{mapping_stats['created']}"
            )

            self.stdout.write(
                "MAPPINGS UPDATED: "
                f"{mapping_stats['updated']}"
            )

            self.stdout.write(
                "MAPPINGS UNCHANGED: "
                f"{mapping_stats['unchanged']}"
            )

            self.stdout.write(
                ""
            )

            self.stdout.write(
                "DATABASE INSIDE TRANSACTION"
            )

            self.stdout.write(
                "-" * 100
            )

            self.print_snapshot(
                after_inside
            )

            if dry_run:
                transaction.set_rollback(
                    True
                )

        final = (
            self.database_snapshot()
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            "DATABASE AFTER COMMAND"
        )

        self.stdout.write(
            "-" * 100
        )

        self.print_snapshot(
            final
        )

        if dry_run:
            if final != before:
                raise CommandError(
                    "Dry run rollback failed. "
                    "Database state changed."
                )

            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "DRY RUN: PASS"
                )
            )

            self.stdout.write(
                "DATABASE WRITES: NONE"
            )

        else:
            self.stdout.write(
                ""
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "IMPORT: PASS"
                )
            )

    def load_csv(
        self,
        path,
    ):
        with path.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            return list(
                csv.DictReader(
                    file
                )
            )

    def validate_source_data(
        self,
        interest_rows,
        mapping_rows,
    ):
        self.stdout.write(
            "SOURCE DATA VALIDATION"
        )

        self.stdout.write(
            "-" * 100
        )

        active_careers = tuple(
            Career.objects
            .filter(active=True)
            .order_by(
                "name",
                "id",
            )
        )

        if (
            len(active_careers)
            != self.EXPECTED_CAREERS
        ):
            raise CommandError(
                "Expected "
                f"{self.EXPECTED_CAREERS} "
                "active Careers, found "
                f"{len(active_careers)}."
            )

        active_names = {
            career.name
            for career
            in active_careers
        }

        interest_names = [
            row[
                "interest_name"
            ].strip()
            for row
            in interest_rows
        ]

        if not all(
            interest_names
        ):
            raise CommandError(
                "Interest catalogue contains "
                "a blank name."
            )

        if (
            len(interest_names)
            != len(
                set(
                    interest_names
                )
            )
        ):
            raise CommandError(
                "Interest catalogue contains "
                "duplicate Interest names."
            )

        catalogue_names = set(
            interest_names
        )

        if (
            len(mapping_rows)
            != self.EXPECTED_TOTAL_MAPPINGS
        ):
            raise CommandError(
                "Expected "
                f"{self.EXPECTED_TOTAL_MAPPINGS} "
                "CareerInterest rows, found "
                f"{len(mapping_rows)}."
            )

        rows_by_career = defaultdict(
            list
        )

        seen_pairs = set()

        for row in mapping_rows:
            career_name = (
                row[
                    "career_name"
                ].strip()
            )

            interest_name = (
                row[
                    "interest_name"
                ].strip()
            )

            if (
                career_name
                not in active_names
            ):
                raise CommandError(
                    "Unknown or inactive Career: "
                    f"{career_name}"
                )

            if (
                interest_name
                not in catalogue_names
            ):
                raise CommandError(
                    "CareerInterest references "
                    "unknown Interest: "
                    f"{interest_name}"
                )

            pair = (
                career_name,
                interest_name,
            )

            if pair in seen_pairs:
                raise CommandError(
                    "Duplicate CareerInterest pair: "
                    f"{career_name} -> "
                    f"{interest_name}"
                )

            seen_pairs.add(
                pair
            )

            try:
                weight = int(
                    row[
                        "relevance_weight"
                    ]
                )
            except (
                TypeError,
                ValueError,
            ) as exc:
                raise CommandError(
                    "Invalid relevance weight: "
                    f"{career_name} -> "
                    f"{interest_name}"
                ) from exc

            if weight not in {
                3,
                4,
                5,
            }:
                raise CommandError(
                    "V1 relevance weight must be "
                    "3, 4, or 5."
                )

            if (
                row[
                    "review_status"
                ].strip()
                != "approved"
            ):
                raise CommandError(
                    "Every V1 mapping must "
                    "be approved."
                )

            if (
                row[
                    "source_type"
                ].strip()
                != "gradnavi_review"
            ):
                raise CommandError(
                    "Every V1 mapping must use "
                    "source_type=gradnavi_review."
                )

            if not (
                row[
                    "source_reference"
                ].strip()
            ):
                raise CommandError(
                    "Every V1 mapping requires "
                    "a source_reference."
                )

            rows_by_career[
                career_name
            ].append(
                weight
            )

        if (
            set(
                rows_by_career
            )
            != active_names
        ):
            raise CommandError(
                "Mapping file does not cover "
                "all active Careers."
            )

        for (
            career_name,
            weights,
        ) in rows_by_career.items():
            if (
                len(weights)
                != self.EXPECTED_INTERESTS_PER_CAREER
            ):
                raise CommandError(
                    f"{career_name} has "
                    f"{len(weights)} mappings. "
                    "Expected 10."
                )

            distribution = Counter(
                weights
            )

            if (
                dict(
                    distribution
                )
                != self.EXPECTED_WEIGHT_DISTRIBUTION
            ):
                raise CommandError(
                    f"{career_name} has invalid "
                    "weight distribution: "
                    f"{dict(distribution)}"
                )

            if (
                sum(weights)
                != self.EXPECTED_WEIGHT_TOTAL
            ):
                raise CommandError(
                    f"{career_name} has total "
                    f"weight {sum(weights)}. "
                    "Expected 40."
                )

        self.stdout.write(
            f"ACTIVE CAREERS: "
            f"{len(active_careers)}"
        )

        self.stdout.write(
            f"UNIQUE INTERESTS: "
            f"{len(interest_rows)}"
        )

        self.stdout.write(
            f"CAREER INTEREST MAPPINGS: "
            f"{len(mapping_rows)}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "SOURCE VALIDATION: PASS"
            )
        )

    def import_interests(
        self,
        interest_rows,
    ):
        created = 0
        reused = 0
        updated = 0

        for row in interest_rows:
            name = (
                row[
                    "interest_name"
                ].strip()
            )

            category = (
                row[
                    "category"
                ].strip()
            )

            interest = (
                Interest.objects
                .filter(
                    name=name
                )
                .first()
            )

            if interest is None:
                Interest.objects.create(
                    name=name,
                    category=category,
                )

                created += 1

                continue

            reused += 1

            if (
                interest.category
                != category
            ):
                interest.category = (
                    category
                )

                interest.save(
                    update_fields=[
                        "category",
                        "updated_at",
                    ]
                )

                updated += 1

        return {
            "created": created,
            "reused": reused,
            "updated": updated,
        }

    def import_mappings(
        self,
        mapping_rows,
    ):
        careers = {
            career.name: career
            for career
            in Career.objects.filter(
                active=True
            )
        }

        interests = {
            interest.name: interest
            for interest
            in Interest.objects.all()
        }

        created = 0
        updated = 0
        unchanged = 0

        for row in mapping_rows:
            career = careers[
                row[
                    "career_name"
                ].strip()
            ]

            interest = interests[
                row[
                    "interest_name"
                ].strip()
            ]

            expected = {
                "relevance_weight": int(
                    row[
                        "relevance_weight"
                    ]
                ),
                "review_status": (
                    row[
                        "review_status"
                    ].strip()
                ),
                "source_type": (
                    row[
                        "source_type"
                    ].strip()
                ),
                "source_reference": (
                    row[
                        "source_reference"
                    ].strip()
                ),
            }

            mapping = (
                CareerInterest.objects
                .filter(
                    career=career,
                    interest=interest,
                )
                .first()
            )

            if mapping is None:
                CareerInterest.objects.create(
                    career=career,
                    interest=interest,
                    **expected,
                )

                created += 1

                continue

            changed_fields = []

            for field, expected_value in (
                expected.items()
            ):
                if (
                    getattr(
                        mapping,
                        field,
                    )
                    != expected_value
                ):
                    setattr(
                        mapping,
                        field,
                        expected_value,
                    )

                    changed_fields.append(
                        field
                    )

            if changed_fields:
                changed_fields.append(
                    "updated_at"
                )

                mapping.save(
                    update_fields=(
                        changed_fields
                    )
                )

                updated += 1

            else:
                unchanged += 1

        return {
            "created": created,
            "updated": updated,
            "unchanged": unchanged,
        }

    def validate_database_state(
        self,
        interest_rows,
        mapping_rows,
    ):
        catalogue_names = {
            row[
                "interest_name"
            ].strip()
            for row
            in interest_rows
        }

        database_interest_names = set(
            Interest.objects
            .filter(
                name__in=catalogue_names
            )
            .values_list(
                "name",
                flat=True,
            )
        )

        if (
            database_interest_names
            != catalogue_names
        ):
            raise CommandError(
                "Database is missing one or "
                "more V1 Interest records."
            )

        expected = {}

        for row in mapping_rows:
            key = (
                row[
                    "career_name"
                ].strip(),
                row[
                    "interest_name"
                ].strip(),
            )

            expected[
                key
            ] = {
                "relevance_weight": int(
                    row[
                        "relevance_weight"
                    ]
                ),
                "review_status": (
                    row[
                        "review_status"
                    ].strip()
                ),
                "source_type": (
                    row[
                        "source_type"
                    ].strip()
                ),
                "source_reference": (
                    row[
                        "source_reference"
                    ].strip()
                ),
            }

        actual_rows = (
            CareerInterest.objects
            .filter(
                career__active=True,
                interest__name__in=(
                    catalogue_names
                ),
            )
            .select_related(
                "career",
                "interest",
            )
        )

        actual = {}

        for mapping in actual_rows:
            key = (
                mapping.career.name,
                mapping.interest.name,
            )

            if key not in expected:
                continue

            actual[
                key
            ] = {
                "relevance_weight": (
                    mapping.relevance_weight
                ),
                "review_status": (
                    mapping.review_status
                ),
                "source_type": (
                    mapping.source_type
                ),
                "source_reference": (
                    mapping.source_reference
                ),
            }

        if (
            set(actual)
            != set(expected)
        ):
            missing = sorted(
                set(expected)
                - set(actual)
            )

            raise CommandError(
                "Database is missing expected "
                "CareerInterest mappings: "
                f"{missing[:10]}"
            )

        mismatches = []

        for key in expected:
            if (
                actual[
                    key
                ]
                != expected[
                    key
                ]
            ):
                mismatches.append(
                    key
                )

        if mismatches:
            raise CommandError(
                "Imported CareerInterest values "
                "do not match V1 source data: "
                f"{mismatches[:10]}"
            )

        counts = (
            CareerInterest.objects
            .filter(
                career__active=True,
            )
            .values_list(
                "career__name",
                flat=False,
            )
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            self.style.SUCCESS(
                "DATABASE VALIDATION: PASS"
            )
        )

    def database_snapshot(
        self,
    ):
        return {
            "interests": (
                Interest.objects.count()
            ),
            "career_interests": (
                CareerInterest.objects.count()
            ),
        }

    def print_snapshot(
        self,
        snapshot,
    ):
        self.stdout.write(
            "INTERESTS: "
            f"{snapshot['interests']}"
        )

        self.stdout.write(
            "CAREER INTERESTS: "
            f"{snapshot['career_interests']}"
        )
