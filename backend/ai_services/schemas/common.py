"""
Shared structured data contracts for GradNavi AI services.

WBS 6.2 uses these Pydantic models to define the minimum approved
Student Profile information available to AI-assisted features.

Important privacy rule:
These models intentionally exclude account identifiers, email addresses,
authentication data, personality responses, interests, project URLs,
database IDs, and other fields not required by the current AI operations.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------------------------------------------------------------------------
# Shared limits
# ---------------------------------------------------------------------------
#
# These limits are GradNavi application rules.
#
# They give the AI boundary predictable request sizes and prevent accidental
# oversized prompt context.
#

SHORT_TEXT_MAX_LENGTH = 255
DESCRIPTION_MAX_LENGTH = 5_000

MAX_SKILLS = 100
MAX_EDUCATION_RECORDS = 20
MAX_EXPERIENCE_RECORDS = 30
MAX_PROJECTS = 30
MAX_CAREER_GOALS = 10


class AIContractModel(BaseModel):
    """
    Base class for GradNavi AI data contracts.

    extra="forbid"
        Rejects fields that are not explicitly declared.

    strict=True
        Rejects unexpected type coercion where strict validation applies.

    str_strip_whitespace=True
        Removes leading and trailing whitespace from string values.
    """

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )


class StudentSkillContext(AIContractModel):
    """
    One approved Student Skill supplied to an AI-assisted feature.

    The canonical database Skill ID is intentionally excluded.
    """

    name: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    proficiency_level: Literal[
        "foundational",
        "developing",
        "proficient",
        "advanced",
    ]


class EducationContext(AIContractModel):
    """
    One approved education record.

    Internal database identifiers and timestamps are intentionally excluded.
    """

    institution_name: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    qualification: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    field_of_study: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    start_date: date
    end_date: date | None = None

    description: str = Field(
        default="",
        max_length=DESCRIPTION_MAX_LENGTH,
    )

    @model_validator(mode="after")
    def validate_date_order(self):
        """
        Prevent an education end date from occurring before its start date.
        """

        if (
            self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "Education end_date cannot be before start_date."
            )

        return self


class ExperienceContext(AIContractModel):
    """
    One approved employment or professional-experience record.
    """

    job_title: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    company: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    start_date: date
    end_date: date | None = None

    is_current: bool

    description: str = Field(
        default="",
        max_length=DESCRIPTION_MAX_LENGTH,
    )

    @model_validator(mode="after")
    def validate_employment_dates(self):
        """
        Enforce basic consistency for employment dates.

        A current role must not have an end date.
        A completed role must not end before its start date.
        """

        if self.is_current and self.end_date is not None:
            raise ValueError(
                "Current experience must not have an end_date."
            )

        if (
            self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "Experience end_date cannot be before start_date."
            )

        return self


class ProjectContext(AIContractModel):
    """
    One approved Student project supplied to an AI-assisted feature.

    project_url is intentionally excluded from the external AI context.
    """

    name: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    description: str = Field(
        default="",
        max_length=DESCRIPTION_MAX_LENGTH,
    )

    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_order(self):
        """
        Prevent a project end date from occurring before its start date.
        """

        if (
            self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "Project end_date cannot be before start_date."
            )

        return self


class CareerGoalContext(AIContractModel):
    """
    One approved Student career goal.

    A career goal describes an intended future direction.
    It must never be treated as past employment experience.
    """

    target_role: str = Field(
        min_length=1,
        max_length=SHORT_TEXT_MAX_LENGTH,
    )

    description: str = Field(
        default="",
        max_length=DESCRIPTION_MAX_LENGTH,
    )


class StudentProfileContext(AIContractModel):
    """
    Minimum approved Student Profile context available to AI features.

    All sections are required as containers but may contain zero records.

    The model deliberately excludes identity, authentication, internal
    database, personality, interest, and unrelated account information.
    """

    skills: list[StudentSkillContext] = Field(
        max_length=MAX_SKILLS,
    )

    education: list[EducationContext] = Field(
        max_length=MAX_EDUCATION_RECORDS,
    )

    experience: list[ExperienceContext] = Field(
        max_length=MAX_EXPERIENCE_RECORDS,
    )

    projects: list[ProjectContext] = Field(
        max_length=MAX_PROJECTS,
    )

    career_goals: list[CareerGoalContext] = Field(
        max_length=MAX_CAREER_GOALS,
    )