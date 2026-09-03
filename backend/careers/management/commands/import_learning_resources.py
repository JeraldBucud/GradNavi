from collections import Counter
from csv import DictReader
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator
from django.db import transaction

from profiles.models import Skill
from careers.models import (
    LearningResource,
    LearningResourceSkill,
)


class Command(BaseCommand):
    """Import controlled WBS 5.7 learning-resource reference data."""

    help = (
        "Import controlled WBS 5.7 learning resources "
        "and canonical Skill mappings."
    )

    RESOURCE_FILE_NAME = "learning_resources.csv"
    MAPPING_FILE_NAME = "learning_resource_skills.csv"
    CANONICAL_SKILLS_FILE_NAME = "canonical_skills.csv"

    RESOURCE_HEADERS = {
        "resource_key",
        "title",
        "provider",
        "url",
        "resource_type",
        "description",
        "is_active",
    }
    MAPPING_HEADERS = {
        "resource_key",
        "canonical_skill_key",
    }
    CANONICAL_SKILL_HEADERS = {
        "canonical_key",
        "name",
    }
    REQUIRED_RESOURCE_FIELDS = {
        "resource_key",
        "title",
        "provider",
        "url",
        "resource_type",
        "is_active",
    }
    REQUIRED_MAPPING_FIELDS = {
        "resource_key",
        "canonical_skill_key",
    }
    VALID_RESOURCE_TYPES = set(
        LearningResource.ResourceType.values
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Run validation and import logic, then roll "
                "back all learning-resource database changes."
            ),
        )
        parser.add_argument(
            "--project-root",
            help=(
                "Override project root. Intended for focused "
                "importer tests; defaults to the repository root."
            ),
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        project_root = self.get_project_root(
            options.get("project_root")
        )
        learning_dir = (
            project_root
            / "data"
            / "reference"
            / "learning"
        )
        canonical_skills_file = (
            project_root
            / "data"
            / "reference"
            / "curated"
            / self.CANONICAL_SKILLS_FILE_NAME
        )

        resource_rows = self.load_csv(
            learning_dir
            / self.RESOURCE_FILE_NAME
        )
        mapping_rows = self.load_csv(
            learning_dir
            / self.MAPPING_FILE_NAME
        )
        canonical_rows = self.load_csv(
            canonical_skills_file
        )

        self.validate_headers(
            self.RESOURCE_FILE_NAME,
            resource_rows,
            self.RESOURCE_HEADERS,
        )
        self.validate_headers(
            self.MAPPING_FILE_NAME,
            mapping_rows,
            self.MAPPING_HEADERS,
        )
        self.validate_headers(
            self.CANONICAL_SKILLS_FILE_NAME,
            canonical_rows,
            self.CANONICAL_SKILL_HEADERS,
        )

        resources_by_key = self.validate_resources(
            resource_rows
        )
        canonical_name_by_key = (
            self.validate_canonical_skills(
                canonical_rows
            )
        )
        resolved_mappings = self.validate_mappings(
            mapping_rows=mapping_rows,
            resources_by_key=resources_by_key,
            canonical_name_by_key=(
                canonical_name_by_key
            ),
        )

        database_snapshot_before = (
            self.database_snapshot()
        )

        resource_created = 0
        resource_updated = 0
        resource_unchanged = 0
        link_created = 0
        link_existing = 0

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN: database changes will be rolled back."
                )
            )

        with transaction.atomic():
            resources_by_resource_key = {}

            for resource_key in sorted(
                resources_by_key
            ):
                row = resources_by_key[
                    resource_key
                ]
                resource = (
                    LearningResource.objects
                    .filter(
                        url=row["url"],
                    )
                    .first()
                )

                if resource is None:
                    resource = (
                        LearningResource.objects
                        .create(
                            title=row["title"],
                            provider=row[
                                "provider"
                            ],
                            url=row["url"],
                            resource_type=row[
                                "resource_type"
                            ],
                            description=row[
                                "description"
                            ],
                            is_active=row[
                                "is_active"
                            ],
                        )
                    )
                    resource_created += 1

                elif self.resource_matches_row(
                    resource,
                    row,
                ):
                    resource_unchanged += 1
                else:
                    resource.title = row["title"]
                    resource.provider = row[
                        "provider"
                    ]
                    resource.resource_type = row[
                        "resource_type"
                    ]
                    resource.description = row[
                        "description"
                    ]
                    resource.is_active = row[
                        "is_active"
                    ]
                    resource.save(
                        update_fields=[
                            "title",
                            "provider",
                            "resource_type",
                            "description",
                            "is_active",
                            "updated_at",
                        ]
                    )
                    resource_updated += 1

                resources_by_resource_key[
                    resource_key
                ] = resource

            for resource_key, skill in resolved_mappings:
                _, created = (
                    LearningResourceSkill.objects
                    .get_or_create(
                        learning_resource=(
                            resources_by_resource_key[
                                resource_key
                            ]
                        ),
                        skill=skill,
                    )
                )
                if created:
                    link_created += 1
                else:
                    link_existing += 1

            if dry_run:
                transaction.set_rollback(True)

        if dry_run:
            database_snapshot_after = (
                self.database_snapshot()
            )

            if (
                database_snapshot_after
                != database_snapshot_before
            ):
                raise CommandError(
                    "Dry-run rollback validation failed. "
                    f"Before={database_snapshot_before}, "
                    f"after={database_snapshot_after}."
                )

            self.stdout.write(
                self.style.SUCCESS(
                    "DRY RUN PASSED: all learning-resource "
                    "changes were rolled back."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "WBS 5.7 learning resources imported."
                )
            )

        self.stdout.write(
            f"Resources created: {resource_created}"
        )
        self.stdout.write(
            f"Resources updated: {resource_updated}"
        )
        self.stdout.write(
            f"Resources unchanged: {resource_unchanged}"
        )
        self.stdout.write(
            f"Links created: {link_created}"
        )
        self.stdout.write(
            f"Links existing: {link_existing}"
        )

    def get_project_root(self, override):
        if override:
            return Path(override).resolve()

        return Path(__file__).resolve().parents[4]

    def load_csv(self, path):
        if not path.exists():
            raise CommandError(
                f"Required WBS 5.7 file is missing: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            return list(DictReader(file))

    def validate_headers(
        self,
        file_name,
        rows,
        required_headers,
    ):
        if not rows:
            raise CommandError(
                f"{file_name} must contain at least one data row."
            )

        fieldnames = set(rows[0].keys())
        missing_headers = (
            required_headers
            - fieldnames
        )

        if missing_headers:
            raise CommandError(
                f"{file_name} is missing required headers: "
                f"{sorted(missing_headers)}."
            )

    def validate_resources(self, rows):
        keys = Counter()
        urls = Counter()
        resources_by_key = {}
        validate_url = URLValidator()

        for line_number, row in enumerate(
            rows,
            start=2,
        ):
            cleaned = {
                key: (row.get(key) or "").strip()
                for key in self.RESOURCE_HEADERS
            }

            for field_name in self.REQUIRED_RESOURCE_FIELDS:
                if not cleaned[field_name]:
                    raise CommandError(
                        f"{self.RESOURCE_FILE_NAME} line "
                        f"{line_number}: {field_name} must not be blank."
                    )

            resource_key = cleaned[
                "resource_key"
            ]
            keys[resource_key] += 1

            url = cleaned["url"]
            urls[url] += 1

            try:
                validate_url(url)
            except ValidationError as error:
                raise CommandError(
                    f"{self.RESOURCE_FILE_NAME} line "
                    f"{line_number}: invalid url {url!r}."
                ) from error

            resource_type = cleaned[
                "resource_type"
            ]
            if (
                resource_type
                not in self.VALID_RESOURCE_TYPES
            ):
                raise CommandError(
                    f"{self.RESOURCE_FILE_NAME} line "
                    f"{line_number}: invalid resource_type "
                    f"{resource_type!r}."
                )

            cleaned["is_active"] = (
                self.parse_boolean(
                    cleaned["is_active"],
                    file_name=self.RESOURCE_FILE_NAME,
                    line_number=line_number,
                    field_name="is_active",
                )
            )
            resources_by_key[
                resource_key
            ] = cleaned

        duplicate_keys = sorted(
            key
            for key, count in keys.items()
            if count > 1
        )
        if duplicate_keys:
            raise CommandError(
                "Duplicate resource_key values in "
                f"{self.RESOURCE_FILE_NAME}: {duplicate_keys}."
            )

        duplicate_urls = sorted(
            url
            for url, count in urls.items()
            if count > 1
        )
        if duplicate_urls:
            raise CommandError(
                "Duplicate url values in "
                f"{self.RESOURCE_FILE_NAME}: {duplicate_urls}."
            )

        return resources_by_key

    def validate_canonical_skills(self, rows):
        canonical_name_by_key = {}

        for line_number, row in enumerate(
            rows,
            start=2,
        ):
            canonical_key = (
                row.get("canonical_key")
                or ""
            ).strip()
            name = (
                row.get("name")
                or ""
            ).strip()

            if not canonical_key:
                raise CommandError(
                    f"{self.CANONICAL_SKILLS_FILE_NAME} line "
                    f"{line_number}: canonical_key must not be blank."
                )
            if not name:
                raise CommandError(
                    f"{self.CANONICAL_SKILLS_FILE_NAME} line "
                    f"{line_number}: name must not be blank."
                )
            if canonical_key in canonical_name_by_key:
                raise CommandError(
                    "Duplicate canonical_key values in "
                    f"{self.CANONICAL_SKILLS_FILE_NAME}: "
                    f"{canonical_key!r}."
                )

            canonical_name_by_key[
                canonical_key
            ] = name

        return canonical_name_by_key

    def validate_mappings(
        self,
        *,
        mapping_rows,
        resources_by_key,
        canonical_name_by_key,
    ):
        pairs = Counter()
        resolved_mappings = []

        for line_number, row in enumerate(
            mapping_rows,
            start=2,
        ):
            cleaned = {
                key: (row.get(key) or "").strip()
                for key in self.MAPPING_HEADERS
            }

            for field_name in self.REQUIRED_MAPPING_FIELDS:
                if not cleaned[field_name]:
                    raise CommandError(
                        f"{self.MAPPING_FILE_NAME} line "
                        f"{line_number}: {field_name} must not be blank."
                    )

            resource_key = cleaned[
                "resource_key"
            ]
            canonical_skill_key = cleaned[
                "canonical_skill_key"
            ]

            if resource_key not in resources_by_key:
                raise CommandError(
                    f"{self.MAPPING_FILE_NAME} line "
                    f"{line_number}: unknown resource_key "
                    f"{resource_key!r}."
                )

            if (
                canonical_skill_key
                not in canonical_name_by_key
            ):
                raise CommandError(
                    f"{self.MAPPING_FILE_NAME} line "
                    f"{line_number}: unknown canonical_skill_key "
                    f"{canonical_skill_key!r}."
                )

            pair = (
                resource_key,
                canonical_skill_key,
            )
            pairs[pair] += 1

            skill_name = canonical_name_by_key[
                canonical_skill_key
            ]
            skill = (
                Skill.objects
                .filter(
                    name=skill_name
                )
                .only(
                    "id",
                    "name",
                )
                .first()
            )

            if skill is None:
                raise CommandError(
                    f"{self.MAPPING_FILE_NAME} line "
                    f"{line_number}: canonical Skill "
                    f"{skill_name!r} is missing from the database."
                )

            resolved_mappings.append(
                (
                    resource_key,
                    skill,
                )
            )

        duplicate_pairs = sorted(
            pair
            for pair, count in pairs.items()
            if count > 1
        )
        if duplicate_pairs:
            raise CommandError(
                "Duplicate resource-skill mappings in "
                f"{self.MAPPING_FILE_NAME}: {duplicate_pairs}."
            )

        return tuple(
            resolved_mappings
        )

    def parse_boolean(
        self,
        value,
        *,
        file_name,
        line_number,
        field_name,
    ):
        normalized = value.casefold()
        if normalized in {
            "true",
            "yes",
            "y",
            "1",
        }:
            return True
        if normalized in {
            "false",
            "no",
            "n",
            "0",
        }:
            return False

        raise CommandError(
            f"{file_name} line {line_number}: invalid "
            f"{field_name} boolean value {value!r}."
        )

    def resource_matches_row(
        self,
        resource,
        row,
    ):
        return (
            resource.title == row["title"]
            and resource.provider == row["provider"]
            and resource.resource_type == row["resource_type"]
            and resource.description == row["description"]
            and resource.is_active == row["is_active"]
        )

    def database_snapshot(self):
        return {
            "learning_resources": tuple(
                LearningResource.objects
                .order_by(
                    "url",
                )
                .values_list(
                    "url",
                    "title",
                    "provider",
                    "resource_type",
                    "description",
                    "is_active",
                )
            ),
            "learning_resource_skills": tuple(
                LearningResourceSkill.objects
                .select_related(
                    "learning_resource",
                    "skill",
                )
                .order_by(
                    "learning_resource__url",
                    "skill__name",
                )
                .values_list(
                    "learning_resource__url",
                    "skill__name",
                )
            ),
        }
