from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Student profile for {self.user}"


class Skill(models.Model):
    """
    Canonical Skill reference used by both StudentSkill and CareerSkill.

    A Skill represents one approved GradNavi concept. External labels,
    aliases, and external identifiers are mapped to this canonical record
    instead of creating duplicate Skill concepts.
    """

    class ConceptType(models.TextChoices):
        SKILL = "skill", "Skill"
        KNOWLEDGE = "knowledge", "Knowledge"
        TECHNOLOGY = "technology", "Technology"

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    concept_type = models.CharField(
        max_length=20,
        choices=ConceptType.choices,
        default=ConceptType.SKILL,
    )

    category = models.CharField(
        max_length=100,
        blank=True,
    )

    description = models.TextField(
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
            models.CheckConstraint(
                condition=models.Q(
                    concept_type__in=[
                        "skill",
                        "knowledge",
                        "technology",
                    ],
                ),
                name="valid_skill_concept_type",
            ),
        ]

    def __str__(self):
        return self.name


class StudentSkill(models.Model):
    class ProficiencyLevel(models.TextChoices):
        FOUNDATIONAL = "foundational", "Foundational"
        DEVELOPING = "developing", "Developing"
        PROFICIENT = "proficient", "Proficient"
        ADVANCED = "advanced", "Advanced"

    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="student_skills",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="student_skills",
    )
    proficiency_level = models.CharField(
        max_length=20,
        choices=ProficiencyLevel.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student_profile", "skill"],
                name="unique_student_profile_skill",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    proficiency_level__in=[
                        "foundational",
                        "developing",
                        "proficient",
                        "advanced",
                    ],
                ),
                name="valid_student_skill_proficiency",
            ),
        ]

    def __str__(self):
        return f"{self.student_profile} - {self.skill} ({self.proficiency_level})"


class Interest(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StudentInterest(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="student_interests",
    )
    interest = models.ForeignKey(
        Interest,
        on_delete=models.PROTECT,
        related_name="student_interests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student_profile", "interest"],
                name="unique_student_profile_interest",
            ),
        ]

    def __str__(self):
        return f"{self.student_profile} - {self.interest}"


class Education(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="education",
    )
    institution_name = models.CharField(max_length=255)
    qualification = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.qualification} at {self.institution_name}"


class Experience(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="experience",
    )
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class Project(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_url = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CareerGoal(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="career_goals",
    )
    target_role = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.target_role


class PersonalityResponse(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="personality_responses",
    )
    question_key = models.CharField(max_length=255)
    response_value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question_key}: {self.student_profile}"
