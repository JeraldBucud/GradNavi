from collections import Counter
from csv import DictReader
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
import unicodedata

from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction
from django.db.models import Count

from profiles.models import Skill
from careers.models import (
    Career,
    CareerExternalMapping,
    CareerSkill,
    CareerSkillEvidence,
    ReferenceDataset,
    ReferenceSource,
    SkillAlias,
    SkillExternalMapping,
)


class Command(BaseCommand):
    """Import the approved GradNavi Dataset 1.0 reference data."""

    help = (
        "Import the approved GradNavi Dataset 1.0 "
        "career and skill reference data."
    )

    EXPECTED_COUNTS = {
        "source_manifest.csv": 20,
        "careers.csv": 36,
        "source_skill_concepts.csv": 2927,
        "canonical_skills.csv": 2873,
        "skill_aliases.csv": 6670,
        "osca_mappings.csv": 36,
        "onet_mappings.csv": 36,
        "esco_mappings.csv": 33,
        "skill_external_mappings.csv": 2927,
        "onet_rating_evidence.csv": 2380,
        "onet_software_evidence.csv": 5992,
        "esco_skill_evidence.csv": 2204,
    }

    EXPECTED_MANIFEST_SOURCES = {
        "ABS OSCA": 4,
        "O*NET Database": 9,
        "ESCO": 7,
    }

    EXPECTED_DATASET_VERSIONS = {
        "ABS OSCA": {"2024 Version 1.0"},
        "O*NET Database": {"31.0"},
        "ESCO": {"1.2.1"},
    }

    EXPECTED_EVIDENCE_COUNTS = {
        "eligible_onet_ratings": 1849,
        "excluded_onet_ratings": 531,
        "eligible_onet_software": 5992,
        "eligible_esco": 2197,
        "excluded_esco": 7,
        "total_eligible": 10038,
    }

    EXPECTED_CAREER_MAPPING_COUNTS = {
        "ABS OSCA": 36,
        "O*NET Database": 36,
        "ESCO": 33,
    }

    EXPECTED_CAREER_MAPPING_TOTAL = 105

    EXPECTED_SKILL_TYPES = {
        "knowledge": 554,
        "skill": 776,
        "technology": 1543,
    }

    EXPECTED_SKILL_MAPPING_COUNTS = {
        "O*NET Database": 1628,
        "ESCO": 1299,
    }

    EXPECTED_CAREER_SKILLS = 9959
    EXPECTED_CAREER_SKILL_EVIDENCE = 10038

    EXPECTED_REQUIREMENT_TYPES = {
        "essential": 1037,
        "optional": 1160,
        "unspecified": 7762,
    }

    EXPECTED_EVIDENCE_SOURCE_COUNTS = {
        "O*NET Database": 7841,
        "ESCO": 2197,
    }

    EXPECTED_CROSS_TYPE_RESOLUTIONS = {
        ("knowledge", "technology"): 82,
    }

    VALID_MAPPING_METHODS = {
        "exact_code",
        "official_crosswalk",
        "exact_title",
        "normalized_title",
        "manual",
    }

    REFERENCE_SOURCE_DEFINITIONS = [
        {
            "name": "ABS OSCA",
            "homepage_url": "https://www.abs.gov.au/",
            "licence_name": "Creative Commons Attribution 4.0 International",
            "licence_url": "https://www.abs.gov.au/privacy-and-legals",
        },
        {
            "name": "Jobs and Skills Australia",
            "homepage_url": "https://www.jobsandskills.gov.au/",
            "licence_name": "Creative Commons Attribution 4.0 International",
            "licence_url": (
                "https://www.jobsandskills.gov.au/copyright-and-disclaimer"
            ),
        },
        {
            "name": "O*NET Database",
            "homepage_url": "https://www.onetcenter.org/",
            "licence_name": "Creative Commons Attribution 4.0 International",
            "licence_url": "https://www.onetcenter.org/license_db.html",
        },
        {
            "name": "ESCO",
            "homepage_url": "https://esco.ec.europa.eu/",
            "licence_name": "",
            "licence_url": "",
        },
    ]

    REFERENCE_DATASET_DEFINITIONS = [
        {
            "source_name": "ABS OSCA",
            "version": "2024 Version 1.0",
            "retrieved_at": date(2026, 8, 29),
            "download_url": (
                "https://www.abs.gov.au/statistics/classifications/"
                "osca-occupation-standard-classification-australia/"
                "2024-version-1-0/data-downloads"
            ),
            "checksum": "",
            "status": "active",
        },
        {
            "source_name": "O*NET Database",
            "version": "31.0",
            "retrieved_at": date(2026, 8, 30),
            "download_url": "https://www.onetcenter.org/database.html",
            "checksum": "",
            "status": "active",
        },
        {
            "source_name": "ESCO",
            "version": "1.2.1",
            "retrieved_at": date(2026, 8, 30),
            "download_url": "https://esco.ec.europa.eu/en/use-esco/download",
            "checksum": "",
            "status": "active",
        },
    ]

    def add_arguments(self, parser):
        """
        Add management command options.
        """

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Run the full Dataset 1.0 import and validation, "
                "then roll back all database changes."
            ),
        )

    def handle(self, *args, **options):
        """
        Validate Dataset 1.0 and run the full import in one outer transaction.
        """

        dry_run = options["dry_run"]

        project_root = Path(__file__).resolve().parents[4]
        curated_dir = project_root / "data" / "reference" / "curated"
        mappings_dir = project_root / "data" / "reference" / "mappings"

        files = {
            "source_manifest.csv": curated_dir / "source_manifest.csv",
            "careers.csv": curated_dir / "careers.csv",
            "source_skill_concepts.csv": curated_dir / "source_skill_concepts.csv",
            "canonical_skills.csv": curated_dir / "canonical_skills.csv",
            "skill_aliases.csv": curated_dir / "skill_aliases.csv",
            "osca_mappings.csv": mappings_dir / "osca_mappings.csv",
            "onet_mappings.csv": mappings_dir / "onet_mappings.csv",
            "esco_mappings.csv": mappings_dir / "esco_mappings.csv",
            "skill_external_mappings.csv": mappings_dir / "skill_external_mappings.csv",
            "onet_rating_evidence.csv": curated_dir / "onet_rating_evidence.csv",
            "onet_software_evidence.csv": curated_dir / "onet_software_evidence.csv",
            "esco_skill_evidence.csv": curated_dir / "esco_skill_evidence.csv",
        }

        self.stdout.write("=" * 100)
        self.stdout.write("GRADNAVI DATASET 1.0 VALIDATION")
        self.stdout.write("=" * 100)
        self.stdout.write("")

        loaded = {}

        for file_name, path in files.items():
            if not path.exists():
                raise CommandError(
                    f"Required Dataset 1.0 file is missing: {path}"
                )

            loaded[file_name] = self.load_csv(path)

        self.stdout.write("1. FILE ROW COUNTS")
        self.stdout.write("-" * 100)

        for file_name, expected_count in self.EXPECTED_COUNTS.items():
            self.validate_equal(
                file_name,
                len(loaded[file_name]),
                expected_count,
            )

        self.stdout.write("")
        self.validate_manifest(
            loaded["source_manifest.csv"]
        )

        self.stdout.write("")
        self.validate_evidence(
            loaded["onet_rating_evidence.csv"],
            loaded["onet_software_evidence.csv"],
            loaded["esco_skill_evidence.csv"],
        )

        self.stdout.write("")
        self.validate_mapping_files(
            loaded["osca_mappings.csv"],
            loaded["onet_mappings.csv"],
            loaded["esco_mappings.csv"],
            loaded["skill_external_mappings.csv"],
        )

        database_counts_before = self.database_count_snapshot()

        if dry_run:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN: database changes will be rolled back."
                )
            )

        with transaction.atomic():
            self.stdout.write("")
            self.import_reference_provenance()

            self.stdout.write("")
            self.import_careers(
                loaded["careers.csv"]
            )

            self.stdout.write("")
            self.import_career_mappings(
                osca_rows=loaded["osca_mappings.csv"],
                onet_rows=loaded["onet_mappings.csv"],
                esco_rows=loaded["esco_mappings.csv"],
            )

            self.stdout.write("")
            canonical_by_key = self.import_skills(
                loaded["canonical_skills.csv"]
            )

            self.stdout.write("")
            self.import_skill_aliases(
                alias_rows=loaded["skill_aliases.csv"],
                canonical_by_key=canonical_by_key,
            )

            self.stdout.write("")
            self.import_skill_external_mappings(
                mapping_rows=loaded["skill_external_mappings.csv"],
                canonical_by_key=canonical_by_key,
            )

            self.stdout.write("")
            self.import_career_skills_and_evidence(
                rating_rows=loaded["onet_rating_evidence.csv"],
                software_rows=loaded["onet_software_evidence.csv"],
                esco_rows=loaded["esco_skill_evidence.csv"],
                skill_mapping_rows=loaded["skill_external_mappings.csv"],
            )

            self.stdout.write("")
            self.validate_final_database_state()

            if dry_run:
                transaction.set_rollback(True)

        if dry_run:
            database_counts_after = self.database_count_snapshot()

            if database_counts_after != database_counts_before:
                raise CommandError(
                    "Dry-run rollback validation failed. "
                    f"Before={database_counts_before}, "
                    f"after={database_counts_after}."
                )

            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "DRY RUN PASSED: all database changes were rolled back."
                )
            )
        else:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "GRADNAVI DATASET 1.0 STEP 8: PASSED"
                )
            )

    def database_count_snapshot(self):
        """
        Return reference-data table counts for dry-run rollback verification.
        """

        return {
            "reference_sources": ReferenceSource.objects.count(),
            "reference_datasets": ReferenceDataset.objects.count(),
            "careers": Career.objects.count(),
            "career_external_mappings": CareerExternalMapping.objects.count(),
            "skills": Skill.objects.count(),
            "skill_aliases": SkillAlias.objects.count(),
            "skill_external_mappings": SkillExternalMapping.objects.count(),
            "career_skills": CareerSkill.objects.count(),
            "career_skill_evidence": CareerSkillEvidence.objects.count(),
        }

    def validate_final_database_state(self):
        """
        Validate the complete Dataset 1.0 database state before commit.
        """

        self.stdout.write("12. FINAL DATABASE VALIDATION")
        self.stdout.write("-" * 100)

        expected_counts = [
            (
                "ReferenceSource records",
                ReferenceSource.objects.count(),
                4,
            ),
            (
                "ReferenceDataset records",
                ReferenceDataset.objects.count(),
                3,
            ),
            (
                "Career records",
                Career.objects.count(),
                36,
            ),
            (
                "CareerExternalMapping records",
                CareerExternalMapping.objects.count(),
                self.EXPECTED_CAREER_MAPPING_TOTAL,
            ),
            (
                "Skill records",
                Skill.objects.count(),
                2873,
            ),
            (
                "SkillAlias records",
                SkillAlias.objects.count(),
                6670,
            ),
            (
                "SkillExternalMapping records",
                SkillExternalMapping.objects.count(),
                2927,
            ),
            (
                "CareerSkill records",
                CareerSkill.objects.count(),
                self.EXPECTED_CAREER_SKILLS,
            ),
            (
                "CareerSkillEvidence records",
                CareerSkillEvidence.objects.count(),
                self.EXPECTED_CAREER_SKILL_EVIDENCE,
            ),
        ]

        for name, actual, expected in expected_counts:
            self.validate_equal(
                name,
                actual,
                expected,
            )

        requirement_counts = Counter(
            CareerSkill.objects.values_list(
                "requirement_type",
                flat=True,
            )
        )

        if dict(requirement_counts) != self.EXPECTED_REQUIREMENT_TYPES:
            raise CommandError(
                "Final CareerSkill requirement-type totals failed. "
                f"Found {dict(requirement_counts)}."
            )

        for requirement_type, expected in self.EXPECTED_REQUIREMENT_TYPES.items():
            self.validate_equal(
                f"Final {requirement_type} CareerSkills",
                requirement_counts[requirement_type],
                expected,
            )

        evidence_source_counts = Counter(
            evidence.dataset.source.name
            for evidence in CareerSkillEvidence.objects.select_related(
                "dataset__source"
            )
        )

        if dict(evidence_source_counts) != self.EXPECTED_EVIDENCE_SOURCE_COUNTS:
            raise CommandError(
                "Final CareerSkillEvidence source totals failed. "
                f"Found {dict(evidence_source_counts)}."
            )

        for source_name, expected in self.EXPECTED_EVIDENCE_SOURCE_COUNTS.items():
            self.validate_equal(
                f"Final {source_name} evidence",
                evidence_source_counts[source_name],
                expected,
            )

        duplicate_career_skills = (
            CareerSkill.objects.values(
                "career_id",
                "skill_id",
            )
            .annotate(total=Count("id"))
            .filter(total__gt=1)
            .count()
        )

        self.validate_equal(
            "Duplicate CareerSkill pairs",
            duplicate_career_skills,
            0,
        )

        duplicate_evidence = (
            CareerSkillEvidence.objects.values(
                "career_skill_id",
                "dataset_id",
                "external_occupation_id",
                "external_skill_id",
                "source_domain",
                "source_relation",
            )
            .annotate(total=Count("id"))
            .filter(total__gt=1)
            .count()
        )

        self.validate_equal(
            "Duplicate CareerSkillEvidence keys",
            duplicate_evidence,
            0,
        )

        self.validate_equal(
            "Non-approved CareerSkills",
            CareerSkill.objects.exclude(
                review_status="approved"
            ).count(),
            0,
        )

        self.validate_equal(
            "CareerSkills with aggregate importance",
            CareerSkill.objects.filter(
                importance_score__isnull=False
            ).count(),
            0,
        )

        self.validate_equal(
            "CareerSkills with aggregate level",
            CareerSkill.objects.filter(
                required_level_score__isnull=False
            ).count(),
            0,
        )

        self.validate_equal(
            "CareerSkills with proficiency assigned",
            CareerSkill.objects.exclude(
                required_proficiency=""
            ).count(),
            0,
        )

        self.validate_equal(
            "Evidence marked not relevant",
            CareerSkillEvidence.objects.filter(
                not_relevant=True
            ).count(),
            0,
        )

        self.validate_equal(
            "Evidence marked suppress",
            CareerSkillEvidence.objects.filter(
                recommend_suppress=True
            ).count(),
            0,
        )

        self.validate_equal(
            "O*NET evidence with source timestamp",
            CareerSkillEvidence.objects.filter(
                dataset__source__name="O*NET Database",
                source_updated_at__isnull=False,
            ).count(),
            0,
        )

        self.validate_equal(
            "ESCO evidence missing source timestamp",
            CareerSkillEvidence.objects.filter(
                dataset__source__name="ESCO",
                source_updated_at__isnull=True,
            ).count(),
            0,
        )

    def load_csv(self, path):
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(DictReader(file))

    def validate_equal(self, name, actual, expected):
        if actual != expected:
            raise CommandError(
                f"{name} validation failed. Expected {expected}, found {actual}."
            )
        self.stdout.write(self.style.SUCCESS(f"[PASS] {name}: {actual}"))

    def parse_boolean(self, value):
        normalized = (value or "").strip().casefold()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
        raise CommandError(f"Invalid boolean value in Dataset 1.0: {value}")

    def parse_confidence(self, value):
        normalized = (value or "").strip()
        if not normalized:
            return None
        try:
            score = Decimal(normalized)
        except InvalidOperation as error:
            raise CommandError(f"Invalid confidence score: {value}") from error
        if score < 0 or score > 100:
            raise CommandError(f"Confidence score outside 0 to 100: {value}")
        return score


    def parse_nullable_boolean(self, value):
        normalized = (value or "").strip().casefold()
        if not normalized:
            return None
        if normalized in {"true", "y", "yes", "1"}:
            return True
        if normalized in {"false", "n", "no", "0"}:
            return False
        raise CommandError(f"Invalid nullable boolean value: {value}")

    def parse_decimal(self, value):
        normalized = (value or "").strip()
        if not normalized:
            return None
        try:
            return Decimal(normalized)
        except InvalidOperation as error:
            raise CommandError(f"Invalid decimal value: {value}") from error

    def parse_esco_datetime(self, value):
        normalized = (value or "").strip()
        if not normalized:
            raise CommandError("Eligible ESCO evidence has a blank modified_date.")
        try:
            parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
        except ValueError as error:
            raise CommandError(
                f"Invalid ESCO modified_date: {value}"
            ) from error
        if parsed.tzinfo is None:
            raise CommandError(
                f"ESCO modified_date must include a timezone: {value}"
            )
        return parsed

    def normalize_text(self, value):
        return unicodedata.normalize("NFKC", value or "").casefold().strip()

    def validate_manifest(self, rows):
        self.stdout.write("2. SOURCE MANIFEST")
        self.stdout.write("-" * 100)

        source_counts = Counter(row["source"].strip() for row in rows)
        for source_name, expected_count in self.EXPECTED_MANIFEST_SOURCES.items():
            self.validate_equal(
                f"{source_name} files",
                source_counts[source_name],
                expected_count,
            )

        invalid_algorithms = [
            row
            for row in rows
            if row["checksum_algorithm"].strip() != "SHA-256"
        ]
        self.validate_equal("Invalid checksum algorithms", len(invalid_algorithms), 0)

        blank_checksums = [row for row in rows if not row["checksum"].strip()]
        self.validate_equal("Blank checksums", len(blank_checksums), 0)

        versions_by_source = {}
        for row in rows:
            source_name = row["source"].strip()
            version = row["dataset_version"].strip()
            versions_by_source.setdefault(source_name, set()).add(version)

        for source_name, expected_versions in self.EXPECTED_DATASET_VERSIONS.items():
            actual_versions = versions_by_source.get(source_name, set())
            if actual_versions != expected_versions:
                raise CommandError(
                    f"{source_name} version validation failed. "
                    f"Expected {expected_versions}, found {actual_versions}."
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"[PASS] {source_name} versions: {sorted(actual_versions)}"
                )
            )

    def validate_evidence(self, rating_rows, software_rows, esco_rows):
        self.stdout.write("3. SOURCE EVIDENCE")
        self.stdout.write("-" * 100)

        eligible_ratings = [
            row for row in rating_rows if self.parse_boolean(row["score_eligible"])
        ]
        eligible_software = [
            row for row in software_rows if self.parse_boolean(row["score_eligible"])
        ]
        eligible_esco = [
            row
            for row in esco_rows
            if self.parse_boolean(row["relationship_eligible"])
        ]

        excluded_ratings = len(rating_rows) - len(eligible_ratings)
        excluded_esco = len(esco_rows) - len(eligible_esco)
        total_eligible = (
            len(eligible_ratings) + len(eligible_software) + len(eligible_esco)
        )

        self.validate_equal(
            "Eligible O*NET ratings",
            len(eligible_ratings),
            self.EXPECTED_EVIDENCE_COUNTS["eligible_onet_ratings"],
        )
        self.validate_equal(
            "Excluded O*NET ratings",
            excluded_ratings,
            self.EXPECTED_EVIDENCE_COUNTS["excluded_onet_ratings"],
        )
        self.validate_equal(
            "Eligible O*NET software",
            len(eligible_software),
            self.EXPECTED_EVIDENCE_COUNTS["eligible_onet_software"],
        )
        self.validate_equal(
            "Eligible ESCO relationships",
            len(eligible_esco),
            self.EXPECTED_EVIDENCE_COUNTS["eligible_esco"],
        )
        self.validate_equal(
            "Excluded ESCO relationships",
            excluded_esco,
            self.EXPECTED_EVIDENCE_COUNTS["excluded_esco"],
        )
        self.validate_equal(
            "Total eligible evidence",
            total_eligible,
            self.EXPECTED_EVIDENCE_COUNTS["total_eligible"],
        )

    def validate_mapping_files(self, osca_rows, onet_rows, esco_rows, skill_rows):
        self.stdout.write("4. APPROVED MAPPINGS")
        self.stdout.write("-" * 100)

        mapping_sets = [
            ("OSCA Career mappings", osca_rows),
            ("O*NET Career mappings", onet_rows),
            ("ESCO Career mappings", esco_rows),
            ("Skill external mappings", skill_rows),
        ]

        for name, rows in mapping_sets:
            non_approved = [
                row for row in rows if row["review_status"].strip() != "approved"
            ]
            self.validate_equal(f"{name} not approved", len(non_approved), 0)

    def import_reference_provenance(self):
        self.stdout.write("5. REFERENCE SOURCE AND DATASET IMPORT")
        self.stdout.write("-" * 100)

        source_created = 0
        source_updated = 0
        source_unchanged = 0
        dataset_created = 0
        dataset_updated = 0
        dataset_unchanged = 0

        with transaction.atomic():
            sources_by_name = {}

            for definition in self.REFERENCE_SOURCE_DEFINITIONS:
                source, created = ReferenceSource.objects.get_or_create(
                    name=definition["name"],
                    defaults={
                        "homepage_url": definition["homepage_url"],
                        "licence_name": definition["licence_name"],
                        "licence_url": definition["licence_url"],
                    },
                )
                sources_by_name[source.name] = source

                if created:
                    source_created += 1
                    continue

                changed_fields = []
                for field_name in ["homepage_url", "licence_name", "licence_url"]:
                    expected_value = definition[field_name]
                    if getattr(source, field_name) != expected_value:
                        setattr(source, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    source.save(update_fields=changed_fields + ["updated_at"])
                    source_updated += 1
                else:
                    source_unchanged += 1

            for definition in self.REFERENCE_DATASET_DEFINITIONS:
                source = sources_by_name[definition["source_name"]]
                dataset, created = ReferenceDataset.objects.get_or_create(
                    source=source,
                    version=definition["version"],
                    defaults={
                        "retrieved_at": definition["retrieved_at"],
                        "download_url": definition["download_url"],
                        "checksum": definition["checksum"],
                        "status": definition["status"],
                    },
                )

                if created:
                    dataset_created += 1
                    continue

                changed_fields = []
                expected_values = {
                    "retrieved_at": definition["retrieved_at"],
                    "download_url": definition["download_url"],
                    "checksum": definition["checksum"],
                    "status": definition["status"],
                }
                for field_name, expected_value in expected_values.items():
                    if getattr(dataset, field_name) != expected_value:
                        setattr(dataset, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    dataset.save(update_fields=changed_fields + ["updated_at"])
                    dataset_updated += 1
                else:
                    dataset_unchanged += 1

            expected_source_names = {
                item["name"] for item in self.REFERENCE_SOURCE_DEFINITIONS
            }
            actual_source_names = set(
                ReferenceSource.objects.values_list("name", flat=True)
            )
            if actual_source_names != expected_source_names:
                raise CommandError("ReferenceSource validation failed after import.")

            expected_dataset_keys = {
                (item["source_name"], item["version"])
                for item in self.REFERENCE_DATASET_DEFINITIONS
            }
            actual_dataset_keys = {
                (dataset.source.name, dataset.version)
                for dataset in ReferenceDataset.objects.select_related("source")
            }
            if actual_dataset_keys != expected_dataset_keys:
                raise CommandError("ReferenceDataset validation failed after import.")

            if ReferenceDataset.objects.filter(
                source__name="Jobs and Skills Australia"
            ).exists():
                raise CommandError(
                    "Jobs and Skills Australia must not have a Dataset 1.0 "
                    "ReferenceDataset."
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"[PASS] ReferenceSource records: {ReferenceSource.objects.count()}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"[PASS] ReferenceDataset records: {ReferenceDataset.objects.count()}"
            )
        )
        self.stdout.write("")
        self.stdout.write(f"ReferenceSources created: {source_created}")
        self.stdout.write(f"ReferenceSources updated: {source_updated}")
        self.stdout.write(f"ReferenceSources unchanged: {source_unchanged}")
        self.stdout.write("")
        self.stdout.write(f"ReferenceDatasets created: {dataset_created}")
        self.stdout.write(f"ReferenceDatasets updated: {dataset_updated}")
        self.stdout.write(f"ReferenceDatasets unchanged: {dataset_unchanged}")

    def import_careers(self, rows):
        self.stdout.write("6. CAREER IMPORT")
        self.stdout.write("-" * 100)

        expected_names = set()
        for row in rows:
            name = row["name"].strip()
            if not name:
                raise CommandError("Blank Career name found.")
            if name in expected_names:
                raise CommandError(f"Duplicate Career name in careers.csv: {name}")
            expected_names.add(name)

        created_count = 0
        updated_count = 0
        unchanged_count = 0

        with transaction.atomic():
            for row in rows:
                name = row["name"].strip()
                expected_values = {
                    "category": row["category"].strip(),
                    "description": row["description"].strip(),
                    "active": self.parse_boolean(row["active"]),
                }
                career, created = Career.objects.get_or_create(
                    name=name,
                    defaults=expected_values,
                )
                if created:
                    created_count += 1
                    continue

                changed_fields = []
                for field_name, expected_value in expected_values.items():
                    if getattr(career, field_name) != expected_value:
                        setattr(career, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    career.save(update_fields=changed_fields + ["updated_at"])
                    updated_count += 1
                else:
                    unchanged_count += 1

            actual_names = set(Career.objects.values_list("name", flat=True))
            if actual_names != expected_names or Career.objects.count() != 36:
                raise CommandError("Career database set does not match careers.csv.")

        self.stdout.write(
            self.style.SUCCESS(f"[PASS] Career records: {Career.objects.count()}")
        )
        self.stdout.write("")
        self.stdout.write(f"Careers created: {created_count}")
        self.stdout.write(f"Careers updated: {updated_count}")
        self.stdout.write(f"Careers unchanged: {unchanged_count}")

    def import_career_mappings(self, osca_rows, onet_rows, esco_rows):
        self.stdout.write("7. CAREER EXTERNAL MAPPING IMPORT")
        self.stdout.write("-" * 100)

        mapping_rows = osca_rows + onet_rows + esco_rows
        self.validate_equal("Career mapping rows", len(mapping_rows), 105)

        source_counts = Counter(row["dataset_source"].strip() for row in mapping_rows)
        if dict(source_counts) != self.EXPECTED_CAREER_MAPPING_COUNTS:
            raise CommandError(
                f"Career mapping source totals failed: {dict(source_counts)}"
            )

        careers_by_name = {career.name: career for career in Career.objects.all()}
        datasets_by_key = {
            (dataset.source.name, dataset.version): dataset
            for dataset in ReferenceDataset.objects.select_related("source")
        }

        planned_keys = set()
        prepared_rows = []

        for row in mapping_rows:
            career_name = row["career_name"].strip()
            dataset_key = (
                row["dataset_source"].strip(),
                row["dataset_version"].strip(),
            )
            external_id = row["external_id"].strip()
            external_title = row["external_title"].strip()
            mapping_method = row["mapping_method"].strip()
            review_status = row["review_status"].strip()
            confidence_score = self.parse_confidence(row["confidence_score"])

            career = careers_by_name.get(career_name)
            dataset = datasets_by_key.get(dataset_key)
            if career is None:
                raise CommandError(f"Unknown Career in mapping: {career_name}")
            if dataset is None:
                raise CommandError(f"Unknown dataset in Career mapping: {dataset_key}")
            if not external_id or not external_title:
                raise CommandError(f"Blank Career mapping value for {career_name}")
            if mapping_method not in self.VALID_MAPPING_METHODS:
                raise CommandError(f"Invalid Career mapping_method: {mapping_method}")
            if review_status != "approved":
                raise CommandError(f"Non-approved Career mapping: {career_name}")

            key = (career.id, dataset.id, external_id)
            if key in planned_keys:
                raise CommandError(f"Duplicate Career mapping key: {key}")
            planned_keys.add(key)
            prepared_rows.append(
                {
                    "career": career,
                    "dataset": dataset,
                    "external_id": external_id,
                    "external_title": external_title,
                    "mapping_method": mapping_method,
                    "review_status": review_status,
                    "confidence_score": confidence_score,
                }
            )

        created_count = 0
        updated_count = 0
        unchanged_count = 0

        with transaction.atomic():
            existing_by_key = {
                (item.career_id, item.dataset_id, item.external_id): item
                for item in CareerExternalMapping.objects.select_for_update().all()
            }
            unexpected = [key for key in existing_by_key if key not in planned_keys]
            if unexpected:
                raise CommandError(
                    "Database contains CareerExternalMapping records outside Dataset 1.0."
                )

            for row in prepared_rows:
                key = (row["career"].id, row["dataset"].id, row["external_id"])
                existing = existing_by_key.get(key)
                if existing is None:
                    CareerExternalMapping.objects.create(**row)
                    created_count += 1
                    continue

                changed_fields = []
                for field_name in [
                    "external_title",
                    "mapping_method",
                    "review_status",
                    "confidence_score",
                ]:
                    expected_value = row[field_name]
                    if getattr(existing, field_name) != expected_value:
                        setattr(existing, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    existing.save(update_fields=changed_fields + ["updated_at"])
                    updated_count += 1
                else:
                    unchanged_count += 1

            final_mappings = list(
                CareerExternalMapping.objects.select_related("dataset__source")
            )
            if len(final_mappings) != 105:
                raise CommandError("Expected 105 CareerExternalMapping records.")
            final_keys = {
                (item.career_id, item.dataset_id, item.external_id)
                for item in final_mappings
            }
            if final_keys != planned_keys:
                raise CommandError("CareerExternalMapping keys failed validation.")

        self.stdout.write(
            self.style.SUCCESS(
                f"[PASS] CareerExternalMapping records: "
                f"{CareerExternalMapping.objects.count()}"
            )
        )
        self.stdout.write("")
        for source_name, count in self.EXPECTED_CAREER_MAPPING_COUNTS.items():
            self.stdout.write(self.style.SUCCESS(f"[PASS] {source_name}: {count}"))
        self.stdout.write("")
        self.stdout.write(f"Career mappings created: {created_count}")
        self.stdout.write(f"Career mappings updated: {updated_count}")
        self.stdout.write(f"Career mappings unchanged: {unchanged_count}")

    def import_skills(self, rows):
        """
        Import the canonical GradNavi Skill catalogue.

        Skills marked preserve_existing keep their approved database
        primary keys. On a clean database, those records are inserted
        first with their approved IDs before normal auto-increment
        Skill creation begins.
        """

        self.stdout.write("8. CANONICAL SKILL IMPORT")
        self.stdout.write("-" * 100)

        canonical_by_key = {}
        normalized_names = set()
        expected_names = set()
        type_counts = Counter()

        preserve_rows = []
        create_rows = []
        expected_preserved_ids = set()

        for row in rows:
            canonical_key = row["canonical_key"].strip()
            name = row["name"].strip()
            concept_type = row["concept_type"].strip()
            import_action = row["import_action"].strip()

            if not canonical_key or canonical_key in canonical_by_key:
                raise CommandError(
                    f"Invalid or duplicate canonical_key: {canonical_key}"
                )

            if not name:
                raise CommandError(
                    f"Blank Skill name for {canonical_key}"
                )

            normalized_name = self.normalize_text(name)
            if normalized_name in normalized_names:
                raise CommandError(
                    f"Duplicate normalized Skill name: {name}"
                )

            normalized_names.add(normalized_name)
            expected_names.add(name)

            if concept_type not in {"skill", "knowledge", "technology"}:
                raise CommandError(
                    f"Invalid Skill concept_type: {concept_type}"
                )

            if import_action not in {"create", "preserve_existing"}:
                raise CommandError(
                    f"Invalid Skill import_action: {import_action}"
                )

            canonical_by_key[canonical_key] = row
            type_counts[concept_type] += 1

            if import_action == "preserve_existing":
                existing_id = row["existing_skill_id"].strip()

                if not existing_id:
                    raise CommandError(
                        "preserve_existing Skill has no existing_skill_id: "
                        f"{name}"
                    )

                try:
                    preserved_id = int(existing_id)
                except ValueError as error:
                    raise CommandError(
                        f"Invalid existing_skill_id for {name}: {existing_id}"
                    ) from error

                if preserved_id in expected_preserved_ids:
                    raise CommandError(
                        f"Duplicate preserved Skill ID: {preserved_id}"
                    )

                expected_preserved_ids.add(preserved_id)
                preserve_rows.append(row)
            else:
                create_rows.append(row)

        if dict(type_counts) != self.EXPECTED_SKILL_TYPES:
            raise CommandError(
                f"Skill type totals failed: {dict(type_counts)}"
            )

        existing_skills = list(Skill.objects.all())
        unexpected_existing = [
            skill.name
            for skill in existing_skills
            if skill.name not in expected_names
        ]

        if unexpected_existing:
            raise CommandError(
                "Database contains Skills outside Dataset 1.0: "
                f"{unexpected_existing[:20]}"
            )

        created_count = 0
        updated_count = 0
        unchanged_count = 0

        with transaction.atomic():
            skills_by_name = {
                skill.name: skill
                for skill in Skill.objects.all()
            }

            id_owner = {
                skill.id: skill.name
                for skill in Skill.objects.all()
            }

            for row in preserve_rows:
                name = row["name"].strip()
                preserved_id = int(
                    row["existing_skill_id"].strip()
                )

                expected_values = {
                    "concept_type": row["concept_type"].strip(),
                    "category": row["category"].strip(),
                    "description": row["description"].strip(),
                }

                skill = skills_by_name.get(name)

                if skill is None:
                    conflicting_name = id_owner.get(preserved_id)

                    if conflicting_name:
                        raise CommandError(
                            f"Preserved Skill ID {preserved_id} for {name} "
                            f"is already used by {conflicting_name}."
                        )

                    skill = Skill.objects.create(
                        id=preserved_id,
                        name=name,
                        **expected_values,
                    )

                    skills_by_name[name] = skill
                    id_owner[preserved_id] = name
                    created_count += 1
                    continue

                if skill.id != preserved_id:
                    raise CommandError(
                        f"Preserved Skill ID mismatch for {name}. "
                        f"Expected {preserved_id}, found {skill.id}."
                    )

                changed_fields = []

                for field_name, expected_value in expected_values.items():
                    if getattr(skill, field_name) != expected_value:
                        setattr(skill, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    skill.save(
                        update_fields=changed_fields + ["updated_at"]
                    )
                    updated_count += 1
                else:
                    unchanged_count += 1

            sequence_sql = connection.ops.sequence_reset_sql(
                no_style(),
                [Skill],
            )

            if sequence_sql:
                with connection.cursor() as cursor:
                    for statement in sequence_sql:
                        cursor.execute(statement)

            for row in create_rows:
                name = row["name"].strip()

                expected_values = {
                    "concept_type": row["concept_type"].strip(),
                    "category": row["category"].strip(),
                    "description": row["description"].strip(),
                }

                skill = skills_by_name.get(name)

                if skill is None:
                    skill = Skill.objects.create(
                        name=name,
                        **expected_values,
                    )

                    skills_by_name[name] = skill
                    id_owner[skill.id] = name
                    created_count += 1
                    continue

                changed_fields = []

                for field_name, expected_value in expected_values.items():
                    if getattr(skill, field_name) != expected_value:
                        setattr(skill, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    skill.save(
                        update_fields=changed_fields + ["updated_at"]
                    )
                    updated_count += 1
                else:
                    unchanged_count += 1

            if Skill.objects.count() != 2873:
                raise CommandError(
                    f"Expected 2873 Skill records, found {Skill.objects.count()}."
                )

            final_names = set(
                Skill.objects.values_list("name", flat=True)
            )

            if final_names != expected_names:
                raise CommandError(
                    "Canonical Skill database set failed validation."
                )

            final_types = Counter(
                Skill.objects.values_list("concept_type", flat=True)
            )

            if dict(final_types) != self.EXPECTED_SKILL_TYPES:
                raise CommandError(
                    f"Database Skill type totals failed: {dict(final_types)}"
                )

            for row in preserve_rows:
                name = row["name"].strip()
                expected_id = int(
                    row["existing_skill_id"].strip()
                )

                actual_id = (
                    Skill.objects.only("id")
                    .get(name=name)
                    .id
                )

                if actual_id != expected_id:
                    raise CommandError(
                        "Final preserved Skill ID validation failed "
                        f"for {name}. Expected {expected_id}, found {actual_id}."
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"[PASS] Skill records: {Skill.objects.count()}"
            )
        )
        self.stdout.write("")
        self.stdout.write(f"Skills created: {created_count}")
        self.stdout.write(f"Skills updated: {updated_count}")
        self.stdout.write(f"Skills unchanged: {unchanged_count}")

        return canonical_by_key


    def import_skill_aliases(self, alias_rows, canonical_by_key):
        self.stdout.write("9. SKILL ALIAS IMPORT")
        self.stdout.write("-" * 100)

        skills_by_name = {skill.name: skill for skill in Skill.objects.all()}
        sources_by_name = {
            source.name: source for source in ReferenceSource.objects.all()
        }

        prepared_rows = []
        planned_keys = set()
        normalized_keys = set()

        for row in alias_rows:
            canonical_key = row["canonical_key"].strip()
            alias = row["alias"].strip()
            source_name = row["source_name"].strip()

            canonical = canonical_by_key.get(canonical_key)
            if canonical is None:
                raise CommandError(f"Unknown canonical_key in alias file: {canonical_key}")

            canonical_name = canonical["name"].strip()
            skill = skills_by_name.get(canonical_name)
            if skill is None:
                raise CommandError(f"Missing canonical Skill: {canonical_name}")
            if not alias:
                raise CommandError(f"Blank alias for {canonical_name}")
            if self.normalize_text(alias) == self.normalize_text(canonical_name):
                raise CommandError(
                    f"Alias duplicates canonical Skill name: {canonical_name} -> {alias}"
                )

            source = None
            if source_name:
                source = sources_by_name.get(source_name)
                if source is None:
                    raise CommandError(f"Unknown ReferenceSource for alias: {source_name}")

            key = (skill.id, alias)
            normalized_key = (skill.id, self.normalize_text(alias))
            if key in planned_keys or normalized_key in normalized_keys:
                raise CommandError(
                    f"Duplicate SkillAlias in Dataset 1.0: {canonical_name} -> {alias}"
                )
            planned_keys.add(key)
            normalized_keys.add(normalized_key)
            prepared_rows.append({"skill": skill, "alias": alias, "source": source})

        created_count = 0
        updated_count = 0
        unchanged_count = 0

        with transaction.atomic():
            existing_by_key = {
                (item.skill_id, item.alias): item
                for item in SkillAlias.objects.select_for_update().all()
            }
            unexpected = [key for key in existing_by_key if key not in planned_keys]
            if unexpected:
                raise CommandError(
                    "Database contains SkillAlias records outside Dataset 1.0."
                )

            objects_to_create = []
            for row in prepared_rows:
                key = (row["skill"].id, row["alias"])
                existing = existing_by_key.get(key)
                if existing is None:
                    objects_to_create.append(SkillAlias(**row))
                    continue

                expected_source_id = row["source"].id if row["source"] else None
                if existing.source_id != expected_source_id:
                    existing.source = row["source"]
                    existing.save(update_fields=["source", "updated_at"])
                    updated_count += 1
                else:
                    unchanged_count += 1

            SkillAlias.objects.bulk_create(objects_to_create, batch_size=500)
            created_count = len(objects_to_create)

            if SkillAlias.objects.count() != 6670:
                raise CommandError(
                    f"Expected 6670 SkillAlias records, found {SkillAlias.objects.count()}."
                )

            final_keys = set(SkillAlias.objects.values_list("skill_id", "alias"))
            if final_keys != planned_keys:
                raise CommandError("SkillAlias database keys failed validation.")

        self.stdout.write(
            self.style.SUCCESS(f"[PASS] SkillAlias records: {SkillAlias.objects.count()}")
        )
        self.stdout.write("")
        self.stdout.write(f"SkillAliases created: {created_count}")
        self.stdout.write(f"SkillAliases updated: {updated_count}")
        self.stdout.write(f"SkillAliases unchanged: {unchanged_count}")

    def import_skill_external_mappings(self, mapping_rows, canonical_by_key):
        self.stdout.write("10. SKILL EXTERNAL MAPPING IMPORT")
        self.stdout.write("-" * 100)

        skills_by_name = {skill.name: skill for skill in Skill.objects.all()}
        datasets_by_key = {
            (dataset.source.name, dataset.version): dataset
            for dataset in ReferenceDataset.objects.select_related("source")
        }

        prepared_rows = []
        planned_keys = set()
        source_counts = Counter()

        for row in mapping_rows:
            canonical_key = row["canonical_key"].strip()
            canonical = canonical_by_key.get(canonical_key)
            if canonical is None:
                raise CommandError(
                    f"Unknown canonical_key in Skill mapping: {canonical_key}"
                )

            skill = skills_by_name.get(canonical["name"].strip())
            if skill is None:
                raise CommandError(f"Missing Skill for mapping: {canonical_key}")

            dataset_key = (
                row["dataset_source"].strip(),
                row["dataset_version"].strip(),
            )
            dataset = datasets_by_key.get(dataset_key)
            if dataset is None:
                raise CommandError(f"Unknown Skill mapping dataset: {dataset_key}")

            external_id = row["external_id"].strip()
            external_label = row["external_label"].strip()
            source_domain = row["source_domain"].strip()
            mapping_method = row["mapping_method"].strip()
            review_status = row["review_status"].strip()
            confidence_score = self.parse_confidence(row["confidence_score"])

            if not external_id or not external_label:
                raise CommandError(f"Blank Skill mapping identifier for {canonical_key}")
            if mapping_method not in self.VALID_MAPPING_METHODS:
                raise CommandError(f"Invalid Skill mapping_method: {mapping_method}")
            if review_status != "approved":
                raise CommandError(f"Non-approved Skill mapping: {external_id}")

            key = (dataset.id, external_id)
            if key in planned_keys:
                raise CommandError(f"Duplicate external Skill mapping key: {key}")
            planned_keys.add(key)
            source_counts[dataset.source.name] += 1

            prepared_rows.append(
                {
                    "skill": skill,
                    "dataset": dataset,
                    "external_id": external_id,
                    "external_label": external_label,
                    "source_domain": source_domain,
                    "mapping_method": mapping_method,
                    "review_status": review_status,
                    "confidence_score": confidence_score,
                }
            )

        if dict(source_counts) != self.EXPECTED_SKILL_MAPPING_COUNTS:
            raise CommandError(f"Skill mapping source totals failed: {dict(source_counts)}")

        created_count = 0
        updated_count = 0
        unchanged_count = 0

        with transaction.atomic():
            existing_by_key = {
                (item.dataset_id, item.external_id): item
                for item in SkillExternalMapping.objects.select_for_update().all()
            }
            unexpected = [key for key in existing_by_key if key not in planned_keys]
            if unexpected:
                raise CommandError(
                    "Database contains SkillExternalMapping records outside Dataset 1.0."
                )

            objects_to_create = []
            for row in prepared_rows:
                key = (row["dataset"].id, row["external_id"])
                existing = existing_by_key.get(key)
                if existing is None:
                    objects_to_create.append(SkillExternalMapping(**row))
                    continue

                changed_fields = []
                expected_values = {
                    "external_label": row["external_label"],
                    "source_domain": row["source_domain"],
                    "mapping_method": row["mapping_method"],
                    "review_status": row["review_status"],
                    "confidence_score": row["confidence_score"],
                }

                if existing.skill_id != row["skill"].id:
                    existing.skill = row["skill"]
                    changed_fields.append("skill")

                for field_name, expected_value in expected_values.items():
                    if getattr(existing, field_name) != expected_value:
                        setattr(existing, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    existing.save(update_fields=changed_fields + ["updated_at"])
                    updated_count += 1
                else:
                    unchanged_count += 1

            SkillExternalMapping.objects.bulk_create(objects_to_create, batch_size=500)
            created_count = len(objects_to_create)

            if SkillExternalMapping.objects.count() != 2927:
                raise CommandError(
                    "Expected 2927 SkillExternalMapping records, found "
                    f"{SkillExternalMapping.objects.count()}."
                )

            final_keys = set(
                SkillExternalMapping.objects.values_list("dataset_id", "external_id")
            )
            if final_keys != planned_keys:
                raise CommandError("SkillExternalMapping keys failed validation.")

            non_approved = SkillExternalMapping.objects.exclude(
                review_status="approved"
            ).count()
            if non_approved:
                raise CommandError(
                    "Database contains non-approved SkillExternalMapping records."
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"[PASS] SkillExternalMapping records: "
                f"{SkillExternalMapping.objects.count()}"
            )
        )
        self.stdout.write("")
        for source_name, count in self.EXPECTED_SKILL_MAPPING_COUNTS.items():
            self.stdout.write(self.style.SUCCESS(f"[PASS] {source_name}: {count}"))
        self.stdout.write("")
        self.stdout.write(f"Skill mappings created: {created_count}")
        self.stdout.write(f"Skill mappings updated: {updated_count}")
        self.stdout.write(f"Skill mappings unchanged: {unchanged_count}")

    def import_career_skills_and_evidence(
        self,
        rating_rows,
        software_rows,
        esco_rows,
        skill_mapping_rows,
    ):
        """
        Import reviewed CareerSkill relationships and source evidence.

        CareerSkill keeps GradNavi's reviewed relationship. O*NET and
        ESCO source-native values stay in CareerSkillEvidence. Aggregate
        CareerSkill scores and proficiency are intentionally unassigned.
        """

        self.stdout.write("11. CAREERSKILL AND EVIDENCE IMPORT")
        self.stdout.write("-" * 100)

        eligible_ratings = [
            row
            for row in rating_rows
            if self.parse_boolean(row["score_eligible"])
        ]
        eligible_software = [
            row
            for row in software_rows
            if self.parse_boolean(row["score_eligible"])
        ]
        eligible_esco = [
            row
            for row in esco_rows
            if self.parse_boolean(row["relationship_eligible"])
        ]

        self.validate_equal("Eligible O*NET rating evidence", len(eligible_ratings), 1849)
        self.validate_equal("Eligible O*NET software evidence", len(eligible_software), 5992)
        self.validate_equal("Eligible ESCO evidence", len(eligible_esco), 2197)

        onet_dataset = ReferenceDataset.objects.select_related("source").get(
            source__name="O*NET Database",
            version="31.0",
        )
        esco_dataset = ReferenceDataset.objects.select_related("source").get(
            source__name="ESCO",
            version="1.2.1",
        )

        careers_by_name = {
            career.name: career
            for career in Career.objects.all()
        }
        if len(careers_by_name) != 36:
            raise CommandError(
                f"Expected 36 Careers before CareerSkill import, "
                f"found {len(careers_by_name)}."
            )

        career_mapping_keys = {
            (mapping.career_id, mapping.dataset_id, mapping.external_id)
            for mapping in CareerExternalMapping.objects.filter(
                dataset__in=[onet_dataset, esco_dataset],
                review_status="approved",
            )
        }

        skill_mappings = list(
            SkillExternalMapping.objects.filter(
                dataset__in=[onet_dataset, esco_dataset],
                review_status="approved",
            ).select_related("skill", "dataset__source")
        )
        skill_mapping_by_key = {
            (mapping.dataset_id, mapping.external_id): mapping
            for mapping in skill_mappings
        }
        if len(skill_mapping_by_key) != len(skill_mappings):
            raise CommandError(
                "Duplicate SkillExternalMapping lookup keys detected."
            )

        mapping_basis_by_key = {}
        for row in skill_mapping_rows:
            key = (
                row["dataset_source"].strip(),
                row["dataset_version"].strip(),
                row["external_id"].strip(),
            )
            if key in mapping_basis_by_key:
                raise CommandError(
                    f"Duplicate Skill mapping basis key: {key}"
                )
            mapping_basis_by_key[key] = row["mapping_basis"].strip()

        pair_relations = {}
        planned_evidence = []
        planned_evidence_keys = set()
        cross_type_counts = Counter()

        def resolve(
            dataset,
            career_name,
            external_occupation_id,
            external_skill_id,
            source_domain,
            source_relation,
            evidence_concept_type,
        ):
            career = careers_by_name.get(career_name)
            if career is None:
                raise CommandError(f"Unknown Career in evidence: {career_name}")

            occupation_key = (
                career.id,
                dataset.id,
                external_occupation_id,
            )
            if occupation_key not in career_mapping_keys:
                raise CommandError(
                    "Missing approved Career occupation mapping: "
                    f"{career_name} -> {external_occupation_id}"
                )

            skill_mapping = skill_mapping_by_key.get(
                (dataset.id, external_skill_id)
            )
            if skill_mapping is None:
                raise CommandError(
                    f"Missing approved Skill mapping: {external_skill_id}"
                )

            skill = skill_mapping.skill

            if evidence_concept_type != skill.concept_type:
                basis_key = (
                    dataset.source.name,
                    dataset.version,
                    external_skill_id,
                )
                mapping_basis = mapping_basis_by_key.get(basis_key, "")
                if mapping_basis != "approved_cross_type_technology_resolution":
                    raise CommandError(
                        "Unapproved cross-type Skill mapping: "
                        f"{career_name} | {external_skill_id} | "
                        f"{evidence_concept_type} -> {skill.concept_type} | "
                        f"basis={mapping_basis}"
                    )
                cross_type_counts[(evidence_concept_type, skill.concept_type)] += 1

            pair = (career.id, skill.id)
            if source_relation:
                pair_relations.setdefault(pair, set()).add(source_relation)

            evidence_key = (
                career.id,
                skill.id,
                dataset.id,
                external_occupation_id,
                external_skill_id,
                source_domain,
                source_relation,
            )
            if evidence_key in planned_evidence_keys:
                raise CommandError(
                    f"Duplicate planned CareerSkillEvidence key: {evidence_key}"
                )
            planned_evidence_keys.add(evidence_key)

            return career, skill, pair

        for row in eligible_ratings:
            career, skill, pair = resolve(
                dataset=onet_dataset,
                career_name=row["career_name"].strip(),
                external_occupation_id=row["onet_soc_code"].strip(),
                external_skill_id=row["external_skill_id"].strip(),
                source_domain=row["source_domain"].strip(),
                source_relation="",
                evidence_concept_type=row["concept_type"].strip(),
            )
            planned_evidence.append(
                {
                    "pair": pair,
                    "dataset": onet_dataset,
                    "external_occupation_id": row["onet_soc_code"].strip(),
                    "external_skill_id": row["external_skill_id"].strip(),
                    "source_domain": row["source_domain"].strip(),
                    "source_relation": "",
                    "raw_importance": self.parse_decimal(row["raw_importance"]),
                    "normalized_importance": self.parse_decimal(
                        row["normalized_importance"]
                    ),
                    "importance_scale_minimum": self.parse_decimal(
                        row["importance_scale_minimum"]
                    ),
                    "importance_scale_maximum": self.parse_decimal(
                        row["importance_scale_maximum"]
                    ),
                    "raw_level": self.parse_decimal(row["raw_level"]),
                    "normalized_level": self.parse_decimal(
                        row["normalized_level"]
                    ),
                    "level_scale_minimum": self.parse_decimal(
                        row["level_scale_minimum"]
                    ),
                    "level_scale_maximum": self.parse_decimal(
                        row["level_scale_maximum"]
                    ),
                    "not_relevant": self.parse_boolean(row["not_relevant"]),
                    "recommend_suppress": self.parse_nullable_boolean(
                        row["recommend_suppress"]
                    ),
                    "source_updated_at": None,
                }
            )

        for row in eligible_software:
            career, skill, pair = resolve(
                dataset=onet_dataset,
                career_name=row["career_name"].strip(),
                external_occupation_id=row["onet_soc_code"].strip(),
                external_skill_id=row["external_skill_id"].strip(),
                source_domain=row["source_domain"].strip(),
                source_relation="",
                evidence_concept_type=row["concept_type"].strip(),
            )
            planned_evidence.append(
                {
                    "pair": pair,
                    "dataset": onet_dataset,
                    "external_occupation_id": row["onet_soc_code"].strip(),
                    "external_skill_id": row["external_skill_id"].strip(),
                    "source_domain": row["source_domain"].strip(),
                    "source_relation": "",
                    "raw_importance": None,
                    "normalized_importance": None,
                    "importance_scale_minimum": None,
                    "importance_scale_maximum": None,
                    "raw_level": None,
                    "normalized_level": None,
                    "level_scale_minimum": None,
                    "level_scale_maximum": None,
                    "not_relevant": False,
                    "recommend_suppress": None,
                    "source_updated_at": None,
                }
            )

        for row in eligible_esco:
            relation_type = row["relation_type"].strip()
            if relation_type not in {"essential", "optional"}:
                raise CommandError(
                    f"Invalid eligible ESCO relation_type: {relation_type}"
                )

            career, skill, pair = resolve(
                dataset=esco_dataset,
                career_name=row["career_name"].strip(),
                external_occupation_id=row["esco_occupation_uri"].strip(),
                external_skill_id=row["external_skill_id"].strip(),
                source_domain=row["source_domain"].strip(),
                source_relation=relation_type,
                evidence_concept_type=row["concept_type"].strip(),
            )
            planned_evidence.append(
                {
                    "pair": pair,
                    "dataset": esco_dataset,
                    "external_occupation_id": row["esco_occupation_uri"].strip(),
                    "external_skill_id": row["external_skill_id"].strip(),
                    "source_domain": row["source_domain"].strip(),
                    "source_relation": relation_type,
                    "raw_importance": None,
                    "normalized_importance": None,
                    "importance_scale_minimum": None,
                    "importance_scale_maximum": None,
                    "raw_level": None,
                    "normalized_level": None,
                    "level_scale_minimum": None,
                    "level_scale_maximum": None,
                    "not_relevant": False,
                    "recommend_suppress": None,
                    "source_updated_at": self.parse_esco_datetime(
                        row["modified_date"]
                    ),
                }
            )

        all_pairs = {row["pair"] for row in planned_evidence}
        self.validate_equal(
            "Planned CareerSkill pairs",
            len(all_pairs),
            self.EXPECTED_CAREER_SKILLS,
        )
        self.validate_equal(
            "Planned CareerSkillEvidence rows",
            len(planned_evidence),
            self.EXPECTED_CAREER_SKILL_EVIDENCE,
        )
        self.validate_equal(
            "Unique planned evidence keys",
            len(planned_evidence_keys),
            self.EXPECTED_CAREER_SKILL_EVIDENCE,
        )

        if dict(cross_type_counts) != self.EXPECTED_CROSS_TYPE_RESOLUTIONS:
            raise CommandError(
                "Cross-type evidence resolution totals failed. "
                f"Found {dict(cross_type_counts)}."
            )
        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] Approved knowledge -> technology resolutions: 82"
            )
        )

        requirement_type_by_pair = {}
        requirement_counts = Counter()
        for pair in all_pairs:
            relations = pair_relations.get(pair, set())
            if not relations:
                requirement_type = "unspecified"
            elif relations == {"essential"}:
                requirement_type = "essential"
            elif relations == {"optional"}:
                requirement_type = "optional"
            else:
                raise CommandError(
                    "Conflicting ESCO requirement types for "
                    f"CareerSkill pair {pair}: {sorted(relations)}"
                )
            requirement_type_by_pair[pair] = requirement_type
            requirement_counts[requirement_type] += 1

        if dict(requirement_counts) != self.EXPECTED_REQUIREMENT_TYPES:
            raise CommandError(
                "CareerSkill requirement totals failed. "
                f"Found {dict(requirement_counts)}."
            )

        career_skill_created = 0
        career_skill_updated = 0
        career_skill_unchanged = 0
        evidence_created = 0
        evidence_updated = 0
        evidence_unchanged = 0

        with transaction.atomic():
            existing_career_skills = {
                (item.career_id, item.skill_id): item
                for item in CareerSkill.objects.select_for_update().all()
            }
            unexpected_pairs = [
                pair
                for pair in existing_career_skills
                if pair not in all_pairs
            ]
            if unexpected_pairs:
                raise CommandError(
                    "Database contains CareerSkill records outside Dataset 1.0. "
                    f"First keys: {unexpected_pairs[:10]}"
                )

            career_skills_to_create = []
            for career_id, skill_id in sorted(all_pairs):
                pair = (career_id, skill_id)
                expected_values = {
                    "importance_score": None,
                    "required_level_score": None,
                    "required_proficiency": "",
                    "requirement_type": requirement_type_by_pair[pair],
                    "review_status": "approved",
                }
                existing = existing_career_skills.get(pair)
                if existing is None:
                    career_skills_to_create.append(
                        CareerSkill(
                            career_id=career_id,
                            skill_id=skill_id,
                            **expected_values,
                        )
                    )
                    continue

                changed_fields = []
                for field_name, expected_value in expected_values.items():
                    if getattr(existing, field_name) != expected_value:
                        setattr(existing, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    existing.save(update_fields=changed_fields + ["updated_at"])
                    career_skill_updated += 1
                else:
                    career_skill_unchanged += 1

            CareerSkill.objects.bulk_create(
                career_skills_to_create,
                batch_size=500,
            )
            career_skill_created = len(career_skills_to_create)

            if CareerSkill.objects.count() != self.EXPECTED_CAREER_SKILLS:
                raise CommandError(
                    "CareerSkill count failed after import. "
                    f"Found {CareerSkill.objects.count()}."
                )

            career_skill_by_pair = {
                (item.career_id, item.skill_id): item
                for item in CareerSkill.objects.all()
            }
            if set(career_skill_by_pair) != all_pairs:
                raise CommandError(
                    "CareerSkill database keys do not match Dataset 1.0."
                )

            saved_requirement_counts = Counter(
                CareerSkill.objects.values_list("requirement_type", flat=True)
            )
            if dict(saved_requirement_counts) != self.EXPECTED_REQUIREMENT_TYPES:
                raise CommandError(
                    "Saved CareerSkill requirement totals failed."
                )

            non_approved_career_skills = CareerSkill.objects.exclude(
                review_status="approved"
            ).count()
            if non_approved_career_skills:
                raise CommandError(
                    "Database contains non-approved CareerSkill records."
                )

            if CareerSkill.objects.filter(importance_score__isnull=False).exists():
                raise CommandError(
                    "CareerSkill importance_score must stay unassigned in Dataset 1.0."
                )
            if CareerSkill.objects.filter(
                required_level_score__isnull=False
            ).exists():
                raise CommandError(
                    "CareerSkill required_level_score must stay unassigned in Dataset 1.0."
                )
            if CareerSkill.objects.exclude(required_proficiency="").exists():
                raise CommandError(
                    "CareerSkill required_proficiency must stay unassigned in Dataset 1.0."
                )

            expected_evidence_rows = []
            expected_evidence_keys = set()
            for row in planned_evidence:
                career_skill = career_skill_by_pair[row["pair"]]
                prepared = {
                    "career_skill": career_skill,
                    "dataset": row["dataset"],
                    "external_occupation_id": row["external_occupation_id"],
                    "external_skill_id": row["external_skill_id"],
                    "source_domain": row["source_domain"],
                    "source_relation": row["source_relation"],
                    "raw_importance": row["raw_importance"],
                    "normalized_importance": row["normalized_importance"],
                    "importance_scale_minimum": row["importance_scale_minimum"],
                    "importance_scale_maximum": row["importance_scale_maximum"],
                    "raw_level": row["raw_level"],
                    "normalized_level": row["normalized_level"],
                    "level_scale_minimum": row["level_scale_minimum"],
                    "level_scale_maximum": row["level_scale_maximum"],
                    "not_relevant": row["not_relevant"],
                    "recommend_suppress": row["recommend_suppress"],
                    "source_updated_at": row["source_updated_at"],
                }
                evidence_key = (
                    career_skill.id,
                    row["dataset"].id,
                    row["external_occupation_id"],
                    row["external_skill_id"],
                    row["source_domain"],
                    row["source_relation"],
                )
                if evidence_key in expected_evidence_keys:
                    raise CommandError(
                        f"Duplicate resolved evidence key: {evidence_key}"
                    )
                expected_evidence_keys.add(evidence_key)
                expected_evidence_rows.append((evidence_key, prepared))

            existing_evidence = {
                (
                    item.career_skill_id,
                    item.dataset_id,
                    item.external_occupation_id,
                    item.external_skill_id,
                    item.source_domain,
                    item.source_relation,
                ): item
                for item in CareerSkillEvidence.objects.select_for_update().all()
            }
            unexpected_evidence = [
                key
                for key in existing_evidence
                if key not in expected_evidence_keys
            ]
            if unexpected_evidence:
                raise CommandError(
                    "Database contains CareerSkillEvidence outside Dataset 1.0. "
                    f"First keys: {unexpected_evidence[:10]}"
                )

            evidence_to_create = []
            evidence_fields = [
                "raw_importance",
                "normalized_importance",
                "importance_scale_minimum",
                "importance_scale_maximum",
                "raw_level",
                "normalized_level",
                "level_scale_minimum",
                "level_scale_maximum",
                "not_relevant",
                "recommend_suppress",
                "source_updated_at",
            ]

            for evidence_key, prepared in expected_evidence_rows:
                existing = existing_evidence.get(evidence_key)
                if existing is None:
                    evidence_to_create.append(
                        CareerSkillEvidence(**prepared)
                    )
                    continue

                changed_fields = []
                for field_name in evidence_fields:
                    expected_value = prepared[field_name]
                    if getattr(existing, field_name) != expected_value:
                        setattr(existing, field_name, expected_value)
                        changed_fields.append(field_name)

                if changed_fields:
                    existing.save(update_fields=changed_fields + ["updated_at"])
                    evidence_updated += 1
                else:
                    evidence_unchanged += 1

            CareerSkillEvidence.objects.bulk_create(
                evidence_to_create,
                batch_size=500,
            )
            evidence_created = len(evidence_to_create)

            if (
                CareerSkillEvidence.objects.count()
                != self.EXPECTED_CAREER_SKILL_EVIDENCE
            ):
                raise CommandError(
                    "CareerSkillEvidence count failed after import. "
                    f"Found {CareerSkillEvidence.objects.count()}."
                )

            final_evidence_keys = {
                (
                    item.career_skill_id,
                    item.dataset_id,
                    item.external_occupation_id,
                    item.external_skill_id,
                    item.source_domain,
                    item.source_relation,
                )
                for item in CareerSkillEvidence.objects.all()
            }
            if final_evidence_keys != expected_evidence_keys:
                raise CommandError(
                    "CareerSkillEvidence database keys do not match Dataset 1.0."
                )

            evidence_source_counts = Counter(
                item.dataset.source.name
                for item in CareerSkillEvidence.objects.select_related(
                    "dataset__source"
                )
            )
            if dict(evidence_source_counts) != self.EXPECTED_EVIDENCE_SOURCE_COUNTS:
                raise CommandError(
                    "CareerSkillEvidence source counts failed. "
                    f"Found {dict(evidence_source_counts)}."
                )

            if CareerSkillEvidence.objects.filter(not_relevant=True).exists():
                raise CommandError(
                    "Imported Dataset 1.0 evidence must not be marked not_relevant."
                )
            if CareerSkillEvidence.objects.filter(recommend_suppress=True).exists():
                raise CommandError(
                    "Imported Dataset 1.0 evidence must not be marked recommend_suppress."
                )
            if CareerSkillEvidence.objects.filter(
                dataset=onet_dataset,
                source_updated_at__isnull=False,
            ).exists():
                raise CommandError(
                    "O*NET evidence source_updated_at must stay blank in Dataset 1.0."
                )
            if CareerSkillEvidence.objects.filter(
                dataset=esco_dataset,
                source_updated_at__isnull=True,
            ).exists():
                raise CommandError(
                    "ESCO evidence must preserve modified_date in source_updated_at."
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"[PASS] CareerSkill records: {CareerSkill.objects.count()}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "[PASS] CareerSkillEvidence records: "
                f"{CareerSkillEvidence.objects.count()}"
            )
        )
        self.stdout.write("")
        for requirement_type, count in self.EXPECTED_REQUIREMENT_TYPES.items():
            self.stdout.write(
                self.style.SUCCESS(
                    f"[PASS] {requirement_type}: {count}"
                )
            )
        self.stdout.write("")
        for source_name, count in self.EXPECTED_EVIDENCE_SOURCE_COUNTS.items():
            self.stdout.write(
                self.style.SUCCESS(
                    f"[PASS] {source_name} evidence: {count}"
                )
            )
        self.stdout.write("")
        self.stdout.write(
            f"CareerSkills created: {career_skill_created}"
        )
        self.stdout.write(
            f"CareerSkills updated: {career_skill_updated}"
        )
        self.stdout.write(
            f"CareerSkills unchanged: {career_skill_unchanged}"
        )
        self.stdout.write("")
        self.stdout.write(
            f"CareerSkillEvidence created: {evidence_created}"
        )
        self.stdout.write(
            f"CareerSkillEvidence updated: {evidence_updated}"
        )
        self.stdout.write(
            f"CareerSkillEvidence unchanged: {evidence_unchanged}"
        )
