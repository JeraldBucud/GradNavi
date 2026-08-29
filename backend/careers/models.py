from django.db import models

from profiles.models import Skill


class MappingMethod(models.TextChoices):
    """
    Describes how an external occupation or Skill record was matched
    to a GradNavi reference record.
    """

    EXACT_CODE = "exact_code", "Exact Code"
    OFFICIAL_CROSSWALK = "official_crosswalk", "Official Crosswalk"
    EXACT_TITLE = "exact_title", "Exact Title"
    NORMALIZED_TITLE = "normalized_title", "Normalized Title"
    MANUAL = "manual", "Manual"


class ReviewStatus(models.TextChoices):
    """
    Describes the review state of imported reference data.

    Only approved reference relationships should enter normal
    recommendation scoring.
    """

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class ReferenceSource(models.Model):
    """
    Represents an external occupational reference organisation
    or classification source.

    Examples:
    - ABS OSCA
    - Jobs and Skills Australia
    - O*NET
    - ESCO
    """

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    homepage_url = models.URLField(
        blank=True,
    )

    licence_name = models.CharField(
        max_length=255,
        blank=True,
    )

    licence_url = models.URLField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name


class ReferenceDataset(models.Model):
    """
    Represents one versioned release of an external reference source.

    Examples:
    - OSCA 2024 Version 1.0
    - O*NET 31.0
    - ESCO 1.2.1
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUPERSEDED = "superseded", "Superseded"

    source = models.ForeignKey(
        ReferenceSource,
        on_delete=models.PROTECT,
        related_name="datasets",
    )

    version = models.CharField(
        max_length=100,
    )

    retrieved_at = models.DateField()

    download_url = models.URLField(
        blank=True,
    )

    checksum = models.CharField(
        max_length=128,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "version"],
                name="unique_reference_source_version",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "active",
                        "superseded",
                    ],
                ),
                name="valid_reference_dataset_status",
            ),
        ]

    def __str__(self):
        return f"{self.source.name} {self.version}"


class Career(models.Model):
    """
    Represents one GradNavi Career.

    External occupation identifiers stay in CareerExternalMapping.
    This keeps GradNavi Career records independent from external
    classification systems.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    category = models.CharField(
        max_length=100,
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name


class CareerExternalMapping(models.Model):
    """
    Connects a GradNavi Career with an external occupation record.

    Possible sources include:
    - OSCA
    - ISCO-08
    - O*NET
    - ESCO
    """

    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="external_mappings",
    )

    dataset = models.ForeignKey(
        ReferenceDataset,
        on_delete=models.PROTECT,
        related_name="career_mappings",
    )

    external_id = models.CharField(
        max_length=255,
    )

    external_title = models.CharField(
        max_length=255,
    )

    mapping_method = models.CharField(
        max_length=30,
        choices=MappingMethod.choices,
    )

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "career",
                    "dataset",
                    "external_id",
                ],
                name="unique_career_external_mapping",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    mapping_method__in=[
                        "exact_code",
                        "official_crosswalk",
                        "exact_title",
                        "normalized_title",
                        "manual",
                    ],
                ),
                name="valid_career_mapping_method",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    review_status__in=[
                        "pending",
                        "approved",
                        "rejected",
                    ],
                ),
                name="valid_career_mapping_review_status",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(confidence_score__isnull=True)
                    | models.Q(
                        confidence_score__gte=0,
                        confidence_score__lte=100,
                    )
                ),
                name="valid_career_mapping_confidence",
            ),
        ]

    def __str__(self):
        return (
            f"{self.career.name} -> "
            f"{self.dataset.source.name}: {self.external_title}"
        )


class SkillAlias(models.Model):
    """
    Stores an alternative label for an existing canonical Skill.

    Aliases support Skill normalisation without creating duplicate
    GradNavi Skill records.
    """

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="aliases",
    )

    alias = models.CharField(
        max_length=255,
    )

    source = models.ForeignKey(
        ReferenceSource,
        on_delete=models.PROTECT,
        related_name="skill_aliases",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "skill",
                    "alias",
                ],
                name="unique_skill_alias",
            ),
        ]

    def __str__(self):
        return f"{self.alias} -> {self.skill.name}"


class SkillExternalMapping(models.Model):
    """
    Connects a canonical GradNavi Skill with an external Skill,
    knowledge, or technology concept.
    """

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="external_mappings",
    )

    dataset = models.ForeignKey(
        ReferenceDataset,
        on_delete=models.PROTECT,
        related_name="skill_mappings",
    )

    external_id = models.CharField(
        max_length=255,
    )

    external_label = models.CharField(
        max_length=255,
    )

    source_domain = models.CharField(
        max_length=100,
        blank=True,
    )

    mapping_method = models.CharField(
        max_length=30,
        choices=MappingMethod.choices,
    )

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "dataset",
                    "external_id",
                ],
                name="unique_external_skill_mapping",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    mapping_method__in=[
                        "exact_code",
                        "official_crosswalk",
                        "exact_title",
                        "normalized_title",
                        "manual",
                    ],
                ),
                name="valid_skill_mapping_method",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    review_status__in=[
                        "pending",
                        "approved",
                        "rejected",
                    ],
                ),
                name="valid_skill_mapping_review_status",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(confidence_score__isnull=True)
                    | models.Q(
                        confidence_score__gte=0,
                        confidence_score__lte=100,
                    )
                ),
                name="valid_skill_mapping_confidence",
            ),
        ]

    def __str__(self):
        return (
            f"{self.skill.name} -> "
            f"{self.dataset.source.name}: {self.external_label}"
        )


class CareerSkill(models.Model):
    """
    Represents GradNavi's reviewed relationship between a Career
    and a canonical Skill.

    CareerSkill stores GradNavi's approved interpretation.

    Source-native evidence stays in CareerSkillEvidence.
    """

    class RequirementType(models.TextChoices):
        ESSENTIAL = "essential", "Essential"
        OPTIONAL = "optional", "Optional"
        UNSPECIFIED = "unspecified", "Unspecified"

    class ProficiencyLevel(models.TextChoices):
        FOUNDATIONAL = "foundational", "Foundational"
        DEVELOPING = "developing", "Developing"
        PROFICIENT = "proficient", "Proficient"
        ADVANCED = "advanced", "Advanced"

    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="career_skills",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="career_skills",
    )

    importance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    required_level_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    required_proficiency = models.CharField(
        max_length=20,
        choices=ProficiencyLevel.choices,
        blank=True,
    )

    requirement_type = models.CharField(
        max_length=20,
        choices=RequirementType.choices,
        default=RequirementType.UNSPECIFIED,
    )

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "career",
                    "skill",
                ],
                name="unique_career_skill",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(importance_score__isnull=True)
                    | models.Q(
                        importance_score__gte=0,
                        importance_score__lte=100,
                    )
                ),
                name="valid_career_skill_importance",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(required_proficiency="")
                    | models.Q(
                        required_proficiency__in=[
                            "foundational",
                            "developing",
                            "proficient",
                            "advanced",
                        ],
                    )
                ),
                name="valid_career_skill_proficiency",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(required_level_score__isnull=True)
                    | models.Q(
                        required_level_score__gte=0,
                        required_level_score__lte=100,
                    )
                ),
                name="valid_career_skill_required_level",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    requirement_type__in=[
                        "essential",
                        "optional",
                        "unspecified",
                    ],
                ),
                name="valid_career_skill_requirement_type",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    review_status__in=[
                        "pending",
                        "approved",
                        "rejected",
                    ],
                ),
                name="valid_career_skill_review_status",
            ),
        ]

    def __str__(self):
        return f"{self.career.name} - {self.skill.name}"


class CareerSkillEvidence(models.Model):
    """
    Preserves source-native evidence supporting a CareerSkill
    relationship.

    Raw values stay available alongside GradNavi-normalized values.
    This provides traceability for reference-data transformations.
    """

    career_skill = models.ForeignKey(
        CareerSkill,
        on_delete=models.CASCADE,
        related_name="evidence",
    )

    dataset = models.ForeignKey(
        ReferenceDataset,
        on_delete=models.PROTECT,
        related_name="career_skill_evidence",
    )

    external_occupation_id = models.CharField(
        max_length=255,
        blank=True,
    )

    external_skill_id = models.CharField(
        max_length=255,
        blank=True,
    )

    source_domain = models.CharField(
        max_length=100,
        blank=True,
    )

    source_relation = models.CharField(
        max_length=100,
        blank=True,
    )

    raw_importance = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )

    normalized_importance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    raw_level = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )

    normalized_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )

    scale_minimum = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )

    scale_maximum = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )

    not_relevant = models.BooleanField(
        default=False,
    )

    recommend_suppress = models.BooleanField(
        blank=True,
        null=True,
    )

    source_updated_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(normalized_importance__isnull=True)
                    | models.Q(
                        normalized_importance__gte=0,
                        normalized_importance__lte=100,
                    )
                ),
                name="valid_evidence_normalized_importance",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(normalized_level__isnull=True)
                    | models.Q(
                        normalized_level__gte=0,
                        normalized_level__lte=100,
                    )
                ),
                name="valid_evidence_normalized_level",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        scale_minimum__isnull=True,
                        scale_maximum__isnull=True,
                    )
                    | models.Q(
                        scale_minimum__isnull=False,
                        scale_maximum__isnull=False,
                        scale_maximum__gt=models.F("scale_minimum"),
                    )
                ),
                name="valid_evidence_scale_range",
            ),
            models.UniqueConstraint(
                fields=[
                    "career_skill",
                    "dataset",
                    "external_occupation_id",
                    "external_skill_id",
                    "source_domain",
                    "source_relation",
                ],
                name="unique_career_skill_evidence",
            ),
        ]

    def __str__(self):
        return (
            f"{self.career_skill} evidence from "
            f"{self.dataset.source.name} {self.dataset.version}"
        )