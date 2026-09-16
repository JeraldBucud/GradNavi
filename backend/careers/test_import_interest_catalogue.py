import csv
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.models import Sum
from django.test import TestCase

from careers.management.commands.import_interest_catalogue import (
    Command,
)
from careers.models import (
    Career,
    CareerInterest,
)
from profiles.models import Interest


class InterestCatalogueImportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        repo_root = (
            Path(__file__)
            .resolve()
            .parents[2]
        )

        cls.data_dir = (
            repo_root
            / "data"
            / "reference"
            / "gradnavi_interests"
            / "v1"
        )

        cls.interest_path = (
            cls.data_dir
            / "interest_catalogue.csv"
        )

        cls.mapping_path = (
            cls.data_dir
            / "career_interest_mappings.csv"
        )

        with cls.mapping_path.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as file:
            mapping_rows = list(
                csv.DictReader(file)
            )

        careers = {}

        for row in mapping_rows:
            career_name = (
                row[
                    "career_name"
                ].strip()
            )

            career_category = (
                row[
                    "career_category"
                ].strip()
            )

            careers[
                career_name
            ] = career_category

        for (
            career_name,
            career_category,
        ) in careers.items():
            Career.objects.create(
                name=career_name,
                category=career_category,
                active=True,
            )

        Interest.objects.create(
            name="Artificial Intelligence",
            category="Technology",
        )

        Interest.objects.create(
            name="Cybersecurity",
            category="Technology",
        )

        Interest.objects.create(
            name="Data Analysis",
            category="Technology",
        )

    def test_source_files_have_locked_counts(self):
        command = Command()

        interest_rows = (
            command.load_csv(
                self.interest_path
            )
        )

        mapping_rows = (
            command.load_csv(
                self.mapping_path
            )
        )

        self.assertEqual(
            len(interest_rows),
            235,
        )

        self.assertEqual(
            len(mapping_rows),
            360,
        )

    def test_dry_run_rolls_back_all_changes(self):
        before_interests = (
            Interest.objects.count()
        )

        before_mappings = (
            CareerInterest.objects.count()
        )

        output = StringIO()

        call_command(
            "import_interest_catalogue",
            dry_run=True,
            stdout=output,
        )

        self.assertEqual(
            Interest.objects.count(),
            before_interests,
        )

        self.assertEqual(
            CareerInterest.objects.count(),
            before_mappings,
        )

        self.assertIn(
            "DRY RUN: PASS",
            output.getvalue(),
        )

        self.assertIn(
            "DATABASE WRITES: NONE",
            output.getvalue(),
        )

    def test_first_import_creates_expected_records(self):
        original_ids = {
            interest.name: interest.pk
            for interest
            in Interest.objects.all()
        }

        output = StringIO()

        call_command(
            "import_interest_catalogue",
            stdout=output,
        )

        self.assertEqual(
            Interest.objects.count(),
            235,
        )

        self.assertEqual(
            CareerInterest.objects.count(),
            360,
        )

        self.assertEqual(
            CareerInterest.objects.filter(
                review_status="approved"
            ).count(),
            360,
        )

        for (
            name,
            original_id,
        ) in original_ids.items():
            self.assertEqual(
                Interest.objects.get(
                    name=name
                ).pk,
                original_id,
            )

        result = output.getvalue()

        self.assertIn(
            "INTERESTS CREATED: 232",
            result,
        )

        self.assertIn(
            "INTERESTS REUSED: 3",
            result,
        )

        self.assertIn(
            "MAPPINGS CREATED: 360",
            result,
        )

        self.assertIn(
            "IMPORT: PASS",
            result,
        )

    def test_second_import_is_no_op(self):
        call_command(
            "import_interest_catalogue",
            stdout=StringIO(),
        )

        mapping_timestamps = {
            mapping.pk: mapping.updated_at
            for mapping
            in CareerInterest.objects.all()
        }

        interest_timestamps = {
            interest.pk: interest.updated_at
            for interest
            in Interest.objects.all()
        }

        output = StringIO()

        call_command(
            "import_interest_catalogue",
            stdout=output,
        )

        self.assertEqual(
            Interest.objects.count(),
            235,
        )

        self.assertEqual(
            CareerInterest.objects.count(),
            360,
        )

        for mapping in (
            CareerInterest.objects.all()
        ):
            self.assertEqual(
                mapping.updated_at,
                mapping_timestamps[
                    mapping.pk
                ],
            )

        for interest in (
            Interest.objects.all()
        ):
            self.assertEqual(
                interest.updated_at,
                interest_timestamps[
                    interest.pk
                ],
            )

        result = output.getvalue()

        self.assertIn(
            "INTERESTS CREATED: 0",
            result,
        )

        self.assertIn(
            "INTERESTS REUSED: 235",
            result,
        )

        self.assertIn(
            "INTERESTS UPDATED: 0",
            result,
        )

        self.assertIn(
            "MAPPINGS CREATED: 0",
            result,
        )

        self.assertIn(
            "MAPPINGS UPDATED: 0",
            result,
        )

        self.assertIn(
            "MAPPINGS UNCHANGED: 360",
            result,
        )

    def test_every_career_has_equal_interest_coverage(self):
        call_command(
            "import_interest_catalogue",
            stdout=StringIO(),
        )

        careers = (
            Career.objects
            .filter(active=True)
            .order_by("name")
        )

        self.assertEqual(
            careers.count(),
            36,
        )

        for career in careers:
            mappings = (
                CareerInterest.objects
                .filter(
                    career=career,
                    review_status="approved",
                )
            )

            self.assertEqual(
                mappings.count(),
                10,
                career.name,
            )

            total_weight = (
                mappings.aggregate(
                    total=Sum(
                        "relevance_weight"
                    )
                )[
                    "total"
                ]
            )

            self.assertEqual(
                total_weight,
                40,
                career.name,
            )

    def test_invalid_source_is_rejected_before_writes(self):
        command = Command()

        interest_rows = (
            command.load_csv(
                self.interest_path
            )
        )

        mapping_rows = (
            command.load_csv(
                self.mapping_path
            )
        )

        mapping_rows[0] = dict(
            mapping_rows[0]
        )

        mapping_rows[0][
            "career_name"
        ] = "Unknown Test Career"

        before_interests = (
            Interest.objects.count()
        )

        before_mappings = (
            CareerInterest.objects.count()
        )

        with self.assertRaises(
            CommandError
        ):
            command.validate_source_data(
                interest_rows,
                mapping_rows,
            )

        self.assertEqual(
            Interest.objects.count(),
            before_interests,
        )

        self.assertEqual(
            CareerInterest.objects.count(),
            before_mappings,
        )

    def test_import_failure_rolls_back_transaction(self):
        before_interests = (
            Interest.objects.count()
        )

        before_mappings = (
            CareerInterest.objects.count()
        )

        with patch.object(
            Command,
            "import_mappings",
            side_effect=RuntimeError(
                "Forced importer failure"
            ),
        ):
            with self.assertRaises(
                RuntimeError
            ):
                call_command(
                    "import_interest_catalogue",
                    stdout=StringIO(),
                )

        self.assertEqual(
            Interest.objects.count(),
            before_interests,
        )

        self.assertEqual(
            CareerInterest.objects.count(),
            before_mappings,
        )
