from django.db import models

from profiles.models import Interest, Skill


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


class CareerInterest(models.Model):
    """
    Reviewed relationship between a GradNavi Career
    and a detailed Student-facing Interest.

    Detailed Interests stay separate from O*NET RIASEC
    occupational-interest evidence.
    """

    class SourceType(models.TextChoices):
        GRADNAVI_REVIEW = (
            "gradnavi_review",
            "GradNavi Review",
        )
        EXTERNAL_EVIDENCE = (
            "external_evidence",
            "External Evidence",
        )

    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="career_interests",
    )

    interest = models.ForeignKey(
        Interest,
        on_delete=models.PROTECT,
        related_name="career_interests",
    )

    relevance_weight = models.PositiveSmallIntegerField()

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.GRADNAVI_REVIEW,
    )

    source_reference = models.TextField(
        blank=True,
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
                    "interest",
                ],
                name="unique_career_interest",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    relevance_weight__gte=1,
                    relevance_weight__lte=5,
                ),
                name="valid_career_interest_relevance",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    review_status__in=[
                        "pending",
                        "approved",
                        "rejected",
                    ],
                ),
                name="valid_career_interest_review_status",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    source_type__in=[
                        "gradnavi_review",
                        "external_evidence",
                    ],
                ),
                name="valid_career_interest_source_type",
            ),
        ]

    def __str__(self):
        return (
            f"{self.career.name} - "
            f"{self.interest.name} "
            f"({self.relevance_weight})"
        )


class CareerRIASECProfile(models.Model):
    """
    Normalized O*NET-style RIASEC evidence for one Career.

    Scores use GradNavi's normalized 0 to 100 scale.

    Source-native evidence stays linked through
    ReferenceDataset and external reference snapshots.
    """

    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="riasec_profiles",
    )

    dataset = models.ForeignKey(
        ReferenceDataset,
        on_delete=models.PROTECT,
        related_name="career_riasec_profiles",
    )

    realistic_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    investigative_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    artistic_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    social_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    enterprising_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    conventional_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    source_reference = models.TextField(
        blank=True,
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
                ],
                name="unique_career_riasec_dataset",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    realistic_score__gte=0,
                    realistic_score__lte=100,
                ),
                name="valid_riasec_realistic_score",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    investigative_score__gte=0,
                    investigative_score__lte=100,
                ),
                name="valid_riasec_investigative_score",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    artistic_score__gte=0,
                    artistic_score__lte=100,
                ),
                name="valid_riasec_artistic_score",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    social_score__gte=0,
                    social_score__lte=100,
                ),
                name="valid_riasec_social_score",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    enterprising_score__gte=0,
                    enterprising_score__lte=100,
                ),
                name="valid_riasec_enterprising_score",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    conventional_score__gte=0,
                    conventional_score__lte=100,
                ),
                name="valid_riasec_conventional_score",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    review_status__in=[
                        "pending",
                        "approved",
                        "rejected",
                    ],
                ),
                name="valid_career_riasec_review_status",
            ),
        ]

    def __str__(self):
        return (
            f"{self.career.name} RIASEC "
            f"({self.dataset})"
        )


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
    Stores source evidence supporting a CareerSkill relationship.

    Evidence records preserve external occupation and skill identifiers,
    raw source ratings, normalized ratings, source-specific scale ranges,
    source quality flags, and source metadata.
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

    importance_scale_minimum = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )

    importance_scale_maximum = models.DecimalField(
        max_digits=10,
        decimal_places=4,
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

    level_scale_minimum = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
    )

    level_scale_maximum = models.DecimalField(
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

    hot_technology = models.BooleanField(
        blank=True,
        null=True,
    )

    in_demand = models.BooleanField(
        blank=True,
        null=True,
    )

    in_demand_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
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
                    models.Q(
                        normalized_importance__isnull=True,
                    )
                    | models.Q(
                        normalized_importance__gte=0,
                        normalized_importance__lte=100,
                    )
                ),
                name="valid_evidence_normalized_importance",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        normalized_level__isnull=True,
                    )
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
                        importance_scale_minimum__isnull=True,
                        importance_scale_maximum__isnull=True,
                    )
                    | models.Q(
                        importance_scale_minimum__isnull=False,
                        importance_scale_maximum__isnull=False,
                        importance_scale_maximum__gt=models.F(
                            "importance_scale_minimum"
                        ),
                    )
                ),
                name="valid_evidence_importance_scale_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        level_scale_minimum__isnull=True,
                        level_scale_maximum__isnull=True,
                    )
                    | models.Q(
                        level_scale_minimum__isnull=False,
                        level_scale_maximum__isnull=False,
                        level_scale_maximum__gt=models.F(
                            "level_scale_minimum"
                        ),
                    )
                ),
                name="valid_evidence_level_scale_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        in_demand_percentage__isnull=True,
                    )
                    | models.Q(
                        in_demand_percentage__gte=0,
                        in_demand_percentage__lte=100,
                    )
                ),
                name="valid_evidence_in_demand_percentage",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        in_demand_percentage__isnull=True,
                    )
                    | models.Q(
                        in_demand=True,
                    )
                ),
                name="evidence_percentage_requires_in_demand",
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
            f"{self.career_skill} - "
            f"{self.dataset} - "
            f"{self.source_domain}"
        )


class LearningResource(models.Model):
    """
    Controlled learning resource reference data for WBS 5.7.

    Resources are linked to canonical GradNavi Skills through
    LearningResourceSkill so learning suggestions are driven by
    reviewed database records rather than fabricated service output.
    """

    class ResourceType(models.TextChoices):
        COURSE = "course", "Course"
        DOCUMENTATION = "documentation", "Documentation"
        ARTICLE = "article", "Article"
        VIDEO = "video", "Video"
        TUTORIAL = "tutorial", "Tutorial"
        BOOK = "book", "Book"
        OTHER = "other", "Other"

    class AccessType(models.TextChoices):
        FREE = "free", "Free"
        FREEMIUM = "freemium", "Freemium"
        PAID = "paid", "Paid"
        UNKNOWN = "unknown", "Unknown"

    class SourceType(models.TextChoices):
        CURATED = "curated", "Curated"
        DISCOVERED = "discovered", "Discovered"

    class HealthStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        NEEDS_REVIEW = "needs_review", "Needs Review"
        BROKEN = "broken", "Broken"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(
        max_length=255,
    )

    resource_key = models.CharField(
        max_length=120,
        unique=True,
    )

    provider = models.CharField(
        max_length=255,
        blank=True,
    )

    url = models.URLField()

    resource_type = models.CharField(
        max_length=30,
        choices=ResourceType.choices,
        default=ResourceType.OTHER,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    access_type = models.CharField(
        max_length=20,
        choices=AccessType.choices,
        default=AccessType.UNKNOWN,
    )

    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.CURATED,
    )

    health_status = models.CharField(
        max_length=20,
        choices=HealthStatus.choices,
        default=HealthStatus.ACTIVE,
    )

    last_checked_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    last_verified_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    skills = models.ManyToManyField(
        Skill,
        through="LearningResourceSkill",
        related_name="learning_resources",
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
                condition=models.Q(
                    resource_type__in=[
                        "course",
                        "documentation",
                        "article",
                        "video",
                        "tutorial",
                        "book",
                        "other",
                    ],
                ),
                name="valid_learning_resource_type",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    access_type__in=[
                        "free",
                        "freemium",
                        "paid",
                        "unknown",
                    ],
                ),
                name="valid_learning_resource_access_type",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    source_type__in=[
                        "curated",
                        "discovered",
                    ],
                ),
                name="valid_learning_resource_source_type",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    health_status__in=[
                        "active",
                        "needs_review",
                        "broken",
                        "archived",
                    ],
                ),
                name="valid_learning_resource_health_status",
            ),
        ]

    def __str__(self):
        return self.title


class LearningResourceSkill(models.Model):
    """
    Links one controlled LearningResource to one canonical Skill.
    """

    learning_resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        related_name="skill_links",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="learning_resource_links",
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
                    "learning_resource",
                    "skill",
                ],
                name="unique_learning_resource_skill",
            ),
        ]

    def __str__(self):
        return (
            f"{self.learning_resource.title} - "
            f"{self.skill.name}"
        )


class LearningResourceDiscoveryAttempt(
    models.Model
):
    """
    Global discovery history for one canonical Skill.

    Discovery state is shared across Students.

    Access filters are intentionally excluded because
    GradNavi discovers one mixed-access catalogue and
    applies Free, Freemium, and Paid filtering later.
    """

    class Status(
        models.TextChoices
    ):
        SUCCESS = (
            "success",
            "Success",
        )

        PARTIAL = (
            "partial",
            "Partial",
        )

        NO_RESULTS = (
            "no_results",
            "No Results",
        )

        PROVIDER_FAILURE = (
            "provider_failure",
            "Provider Failure",
        )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name=(
            "learning_resource_discovery_attempts"
        ),
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
    )

    requested_count = (
        models.PositiveSmallIntegerField()
    )

    candidate_count = (
        models.PositiveSmallIntegerField(
            default=0,
        )
    )

    persisted_count = (
        models.PositiveSmallIntegerField(
            default=0,
        )
    )

    attempted_at = models.DateTimeField(
        auto_now_add=True,
    )

    next_eligible_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "skill",
                    "-attempted_at",
                ],
                name=(
                    "career_lrd_skill_attempt_idx"
                ),
            ),
            models.Index(
                fields=[
                    "skill",
                    "next_eligible_at",
                ],
                name=(
                    "career_lrd_skill_next_idx"
                ),
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "success",
                        "partial",
                        "no_results",
                        "provider_failure",
                    ],
                ),
                name=(
                    "valid_learning_resource_"
                    "discovery_status"
                ),
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        requested_count__gte=1,
                    )
                    &
                    models.Q(
                        requested_count__lte=6,
                    )
                ),
                name=(
                    "valid_learning_resource_"
                    "discovery_request_count"
                ),
            ),
            models.CheckConstraint(
                condition=models.Q(
                    candidate_count__lte=(
                        models.F(
                            "requested_count"
                        )
                    ),
                ),
                name=(
                    "learning_resource_discovery_"
                    "candidates_lte_requested"
                ),
            ),
            models.CheckConstraint(
                condition=models.Q(
                    persisted_count__lte=(
                        models.F(
                            "candidate_count"
                        )
                    ),
                ),
                name=(
                    "learning_resource_discovery_"
                    "persisted_lte_candidates"
                ),
            ),
        ]

    def __str__(
        self,
    ):
        return (
            "Learning Resource discovery: "
            f"{self.skill_id} - "
            f"{self.status}"
        )


class RoadmapProgress(models.Model):
    """
    Stores Student progress against one Career roadmap Skill.

    Progress is linked to the Skill rather than a displayed step number
    because roadmap ordering can change when Student evidence changes.
    """

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    student_profile = models.ForeignKey(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name="roadmap_progress",
    )

    career = models.ForeignKey(
        Career,
        on_delete=models.PROTECT,
        related_name="student_roadmap_progress",
    )

    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="student_roadmap_progress",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED,
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    completed_at = models.DateTimeField(
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
                    "student_profile",
                    "career",
                    "skill",
                ],
                name="unique_student_career_roadmap_skill",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "not_started",
                        "in_progress",
                        "completed",
                    ],
                ),
                name="valid_roadmap_progress_status",
            ),
        ]

    def __str__(self):
        return (
            f"Roadmap progress: "
            f"{self.student_profile_id} - "
            f"{self.career_id} - "
            f"{self.skill_id}"
        )


class RoadmapGuidanceSnapshot(models.Model):
    """
    Stores the latest valid personalised Roadmap guidance for one
    Student Profile and selected Career.

    Raw Student Profile data is not stored here.
    The cache key fingerprints the approved source context.
    """

    student_profile = models.ForeignKey(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name="roadmap_guidance_snapshots",
    )

    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="roadmap_guidance_snapshots",
    )

    cache_key = models.CharField(
        max_length=64,
    )

    guidance_version = models.CharField(
        max_length=50,
    )

    model = models.CharField(
        max_length=100,
        blank=True,
    )

    payload = models.JSONField()

    prompt_tokens = models.PositiveIntegerField(
        default=0,
    )

    total_tokens = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    generated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student_profile",
                    "career",
                ],
                name="unique_roadmap_guidance_snapshot",
            ),
        ]

    def __str__(self):
        return (
            "Roadmap guidance snapshot for "
            f"Student Profile {self.student_profile_id}, "
            f"Career {self.career_id}"
        )


class LearningResourceGuidanceSnapshot(models.Model):
    """
    Stores the latest valid personalised Learning Resource
    guidance for one Student, Career, and Skill.

    The payload contains generated Student-facing explanations.

    Raw Student Profile context is not stored here.
    """

    student_profile = models.ForeignKey(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name=(
            "learning_resource_guidance_snapshots"
        ),
    )

    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name=(
            "learning_resource_guidance_snapshots"
        ),
    )

    skill = models.ForeignKey(
        "profiles.Skill",
        on_delete=models.PROTECT,
        related_name=(
            "learning_resource_guidance_snapshots"
        ),
    )

    cache_key = models.CharField(
        max_length=64,
    )

    guidance_version = models.CharField(
        max_length=50,
    )

    model = models.CharField(
        max_length=100,
        blank=True,
    )

    payload = models.JSONField()

    prompt_tokens = models.PositiveIntegerField(
        default=0,
    )

    total_tokens = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    generated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student_profile",
                    "career",
                    "skill",
                ],
                name=(
                    "unique_learning_resource_"
                    "guidance_snapshot"
                ),
            ),
        ]

    def __str__(self):
        return (
            "Learning Resource guidance snapshot for "
            f"Student Profile {self.student_profile_id}, "
            f"Career {self.career_id}, "
            f"Skill {self.skill_id}"
        )


class LearningResourceFeedback(models.Model):
    """
    Stores one Student's current usefulness response for one resource.

    A Student can change their response later without creating
    duplicate current votes.
    """

    class FeedbackType(models.TextChoices):
        HELPFUL = "helpful", "Helpful"
        NOT_HELPFUL = "not_helpful", "Not Helpful"

    student_profile = models.ForeignKey(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name="learning_resource_feedback",
    )

    learning_resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        related_name="student_feedback",
    )

    feedback_type = models.CharField(
        max_length=20,
        choices=FeedbackType.choices,
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
                    "student_profile",
                    "learning_resource",
                ],
                name="unique_student_learning_resource_feedback",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    feedback_type__in=[
                        "helpful",
                        "not_helpful",
                    ],
                ),
                name="valid_learning_resource_feedback_type",
            ),
        ]

    def __str__(self):
        return (
            f"{self.feedback_type}: "
            f"{self.student_profile_id} - "
            f"{self.learning_resource_id}"
        )


class LearningResourceReport(models.Model):
    """
    Stores Student-reported learning-resource quality issues.

    Reports enter a review workflow. A report does not directly remove
    or archive a learning resource.
    """

    class Reason(models.TextChoices):
        BROKEN_LINK = "broken_link", "Broken Link"
        OUTDATED = "outdated", "Outdated"
        NOT_RELEVANT = "not_relevant", "Not Relevant"
        TOO_DIFFICULT = "too_difficult", "Too Difficult"
        REQUIRES_PAYMENT = (
            "requires_payment",
            "Requires Payment",
        )
        DUPLICATE = "duplicate", "Duplicate"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESOLVED = "resolved", "Resolved"
        DISMISSED = "dismissed", "Dismissed"

    student_profile = models.ForeignKey(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name="learning_resource_reports",
    )

    learning_resource = models.ForeignKey(
        LearningResource,
        on_delete=models.CASCADE,
        related_name="student_reports",
    )

    reason = models.CharField(
        max_length=30,
        choices=Reason.choices,
    )

    comment = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
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
                condition=models.Q(
                    reason__in=[
                        "broken_link",
                        "outdated",
                        "not_relevant",
                        "too_difficult",
                        "requires_payment",
                        "duplicate",
                        "other",
                    ],
                ),
                name="valid_learning_resource_report_reason",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "open",
                        "resolved",
                        "dismissed",
                    ],
                ),
                name="valid_learning_resource_report_status",
            ),
        ]

    def __str__(self):
        return (
            f"{self.reason}: "
            f"{self.learning_resource_id}"
        )



class StudentCareerEvaluation(models.Model):
    """
    Stores one Student's explicit evaluation of one Career.

    Browsing Explore Careers does not create this record.

    The evaluation stays current only while the Student Profile
    fingerprint, Career reference fingerprint, and scoring version
    still match the values used when the Career was evaluated.

    The payload stores the calculated result for the selected Career.
    Raw Student Profile data is not stored here.
    """

    student_profile = models.ForeignKey(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name="career_evaluations",
    )

    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="student_evaluations",
    )

    profile_fingerprint = models.CharField(
        max_length=64,
    )

    reference_fingerprint = models.CharField(
        max_length=64,
    )

    scoring_version = models.CharField(
        max_length=50,
    )

    payload = models.JSONField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    evaluated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student_profile",
                    "career",
                ],
                name=(
                    "unique_student_career_"
                    "evaluation"
                ),
            ),
        ]

    def __str__(self):
        return (
            "Career evaluation for "
            f"Student Profile {self.student_profile_id} "
            f"and Career {self.career_id}"
        )


class RecommendationSnapshot(models.Model):
    """
    Stores the latest valid Career Recommendation result
    for one Student Profile.

    The snapshot contains no raw Student Profile payload.
    Profile state is represented by a SHA-256 fingerprint.

    A cached result stays valid only when:

    - the Student recommendation inputs are unchanged,
    - the Career reference evidence is unchanged,
    - the scoring version is unchanged.
    """

    student_profile = models.OneToOneField(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name="recommendation_snapshot",
    )

    profile_fingerprint = models.CharField(
        max_length=64,
    )

    reference_fingerprint = models.CharField(
        max_length=64,
    )

    scoring_version = models.CharField(
        max_length=50,
    )

    payload = models.JSONField()

    embedding_model = models.CharField(
        max_length=100,
        blank=True,
    )

    prompt_tokens = models.PositiveIntegerField(
        default=0,
    )

    total_tokens = models.PositiveIntegerField(
        default=0,
    )

    career_count = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    generated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            "Career Recommendation snapshot for "
            f"Student Profile {self.student_profile_id}"
        )


class SkillGapSummarySnapshot(models.Model):
    """
    Stores the latest valid AI Gap Summary for one
    Student Profile and selected Career.

    The cache key fingerprints the deterministic
    readiness state and controlled learning-resource state.

    No raw Student Profile payload is stored.
    """

    student_profile = models.ForeignKey(
        "profiles.StudentProfile",
        on_delete=models.CASCADE,
        related_name="skill_gap_summary_snapshots",
    )

    career = models.ForeignKey(
        "Career",
        on_delete=models.CASCADE,
        related_name="skill_gap_summary_snapshots",
    )

    cache_key = models.CharField(
        max_length=64,
    )

    summary_version = models.CharField(
        max_length=50,
    )

    model = models.CharField(
        max_length=100,
    )

    payload = models.JSONField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    generated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student_profile",
                    "career",
                ],
                name=(
                    "unique_skill_gap_summary_"
                    "snapshot"
                ),
            ),
        ]

    def __str__(self):
        return (
            "Skill Gap Summary snapshot for "
            f"Student Profile {self.student_profile_id} "
            f"and Career {self.career_id}"
        )
