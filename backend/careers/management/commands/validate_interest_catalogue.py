import csv
from collections import (
    Counter,
    defaultdict,
)
from pathlib import Path

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from careers.models import (
    Career,
    CareerExternalMapping,
)


EXPECTED_CAREERS = 36

EXPECTED_INTERESTS_PER_CAREER = 10

EXPECTED_TOTAL_MAPPINGS = (
    EXPECTED_CAREERS
    * EXPECTED_INTERESTS_PER_CAREER
)

EXPECTED_WEIGHT_DISTRIBUTION = {
    5: 3,
    4: 4,
    3: 3,
}

EXPECTED_WEIGHT_TOTAL = 40


class Command(BaseCommand):
    help = (
        "Validate the version-controlled "
        "GradNavi Interest catalogue."
    )

    def handle(
        self,
        *args,
        **options,
    ):
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
                "Interest catalogue file "
                "does not exist."
            )

        if not mapping_path.exists():
            raise CommandError(
                "Career Interest mapping file "
                "does not exist."
            )

        with interest_path.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            interest_rows = list(
                csv.DictReader(
                    file
                )
            )

        with mapping_path.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            mapping_rows = list(
                csv.DictReader(
                    file
                )
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
            != EXPECTED_CAREERS
        ):
            raise CommandError(
                "Expected "
                f"{EXPECTED_CAREERS} "
                "active Careers, found "
                f"{len(active_careers)}."
            )

        active_names = {
            career.name
            for career
            in active_careers
        }

        mapping_names = {
            row[
                "career_name"
            ].strip()
            for row
            in mapping_rows
        }

        if (
            active_names
            != mapping_names
        ):
            raise CommandError(
                "Career mapping coverage "
                "does not match active Careers."
            )

        if (
            len(mapping_rows)
            != EXPECTED_TOTAL_MAPPINGS
        ):
            raise CommandError(
                "Expected "
                f"{EXPECTED_TOTAL_MAPPINGS} "
                "mapping rows, found "
                f"{len(mapping_rows)}."
            )

        catalogue_names = [
            row[
                "interest_name"
            ].strip()
            for row
            in interest_rows
        ]

        if (
            len(catalogue_names)
            != len(
                set(
                    catalogue_names
                )
            )
        ):
            raise CommandError(
                "Interest catalogue contains "
                "duplicate names."
            )

        catalogue_name_set = set(
            catalogue_names
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

            pair = (
                career_name,
                interest_name,
            )

            if pair in seen_pairs:
                raise CommandError(
                    "Duplicate CareerInterest: "
                    f"{career_name} -> "
                    f"{interest_name}"
                )

            seen_pairs.add(
                pair
            )

            if (
                interest_name
                not in catalogue_name_set
            ):
                raise CommandError(
                    f"{interest_name} is used "
                    "but missing from the "
                    "Interest catalogue."
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
                    "Invalid relevance weight "
                    f"for {career_name} -> "
                    f"{interest_name}."
                ) from exc

            if weight not in {
                3,
                4,
                5,
            }:
                raise CommandError(
                    "V1 relevance weights "
                    "must be 3, 4, or 5."
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
                    "Every V1 detailed Interest "
                    "mapping must use "
                    "gradnavi_review."
                )

            if not (
                row[
                    "source_reference"
                ].strip()
            ):
                raise CommandError(
                    "Every mapping requires "
                    "a source reference."
                )

            rows_by_career[
                career_name
            ].append(
                (
                    interest_name,
                    weight,
                )
            )

        career_by_name = {
            career.name: career
            for career
            in active_careers
        }

        category_totals = Counter()

        for career_name in sorted(
            rows_by_career,
            key=str.casefold,
        ):
            rows = (
                rows_by_career[
                    career_name
                ]
            )

            if (
                len(rows)
                != EXPECTED_INTERESTS_PER_CAREER
            ):
                raise CommandError(
                    f"{career_name} has "
                    f"{len(rows)} Interests."
                )

            weight_distribution = Counter(
                weight
                for (
                    interest_name,
                    weight,
                )
                in rows
            )

            if (
                dict(
                    weight_distribution
                )
                != EXPECTED_WEIGHT_DISTRIBUTION
            ):
                raise CommandError(
                    f"{career_name} has invalid "
                    "weight distribution: "
                    f"{dict(weight_distribution)}"
                )

            weight_total = sum(
                weight
                for (
                    interest_name,
                    weight,
                )
                in rows
            )

            if (
                weight_total
                != EXPECTED_WEIGHT_TOTAL
            ):
                raise CommandError(
                    f"{career_name} has total "
                    f"Interest weight "
                    f"{weight_total}, expected "
                    f"{EXPECTED_WEIGHT_TOTAL}."
                )

            career = (
                career_by_name[
                    career_name
                ]
            )

            approved_sources = (
                CareerExternalMapping.objects
                .filter(
                    career=career,
                    review_status="approved",
                )
                .count()
            )

            if approved_sources == 0:
                raise CommandError(
                    f"{career_name} has no "
                    "approved occupation "
                    "reference mapping."
                )

            category_totals[
                career.category
            ] += len(
                rows
            )

        expected_category_total = 40

        for category, total in (
            category_totals.items()
        ):
            if (
                total
                != expected_category_total
            ):
                raise CommandError(
                    f"{category} has "
                    f"{total} mappings. "
                    "Expected 40."
                )

        self.stdout.write(
            "=" * 90
        )

        self.stdout.write(
            "GRADNAVI INTEREST CATALOGUE "
            "VALIDATION"
        )

        self.stdout.write(
            "=" * 90
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
            f"TOTAL MAPPINGS: "
            f"{len(mapping_rows)}"
        )

        self.stdout.write(
            "INTERESTS PER CAREER: "
            "10"
        )

        self.stdout.write(
            "WEIGHT DISTRIBUTION: "
            "3x5, 4x4, 3x3"
        )

        self.stdout.write(
            "TOTAL WEIGHT PER CAREER: "
            "40"
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            "CATEGORY COVERAGE:"
        )

        for category in sorted(
            category_totals
        ):
            self.stdout.write(
                f"  {category}: "
                f"{category_totals[category]}"
            )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            self.style.SUCCESS(
                "VALIDATION: PASS"
            )
        )

        self.stdout.write(
            "DATABASE WRITES: NONE"
        )
