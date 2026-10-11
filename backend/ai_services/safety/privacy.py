"""
Privacy allowlist for GradNavi AI-assisted features.

WBS 6.2 must not send complete Django model objects to an external
AI provider.

This module converts an approved StudentProfile into the minimum
StudentProfileContext required by AI-assisted document features.

Important:
Authentication and ownership checks happen before this function is called.
This module does not decide which StudentProfile a user is allowed to access.
"""

from profiles.models import StudentProfile

from ai_services.schemas.common import (
    CareerGoalContext,
    EducationContext,
    ExperienceContext,
    ProjectContext,
    StudentProfileContext,
    StudentSkillContext,
)


# ---------------------------------------------------------------------------
# Approved AI profile fields
# ---------------------------------------------------------------------------
#
# This allowlist documents the only Student Profile areas currently approved
# for AI context.
#
# New database fields must not automatically become AI-visible.
#

AI_PROFILE_ALLOWLIST = (
    "skills",
    "education",
    "experience",
    "projects",
    "career_goals",
)


def build_student_profile_context(
    *,
    student_profile: StudentProfile,
) -> StudentProfileContext:
    """
    Build the minimum approved Student Profile context for AI operations.

    The returned Pydantic model deliberately excludes:

    - User ID
    - StudentProfile ID
    - Email address
    - Account role
    - Password information
    - JWT information
    - Interests
    - Personality responses
    - Project URLs
    - Database timestamps
    - Internal database identifiers

    The caller is responsible for authentication and ownership checks
    before supplying student_profile.
    """

    skills = [
        StudentSkillContext(
            name=student_skill.skill.name,
            proficiency_level=student_skill.proficiency_level,
        )
        for student_skill
        in student_profile.student_skills
        .select_related("skill")
        .order_by("skill__name")
    ]

    education = [
        EducationContext(
            institution_name=record.institution_name,
            qualification=record.qualification,
            field_of_study=record.field_of_study,
            start_date=record.start_date,
            end_date=record.end_date,
            description=record.description,
        )
        for record
        in student_profile.education.order_by(
            "-start_date",
            "-id",
        )
    ]

    experience = [
        ExperienceContext(
            job_title=record.job_title,
            company=record.company,
            start_date=record.start_date,
            end_date=record.end_date,
            is_current=record.is_current,
            description=record.description,
        )
        for record
        in student_profile.experience.order_by(
            "-start_date",
            "-id",
        )
    ]

    projects = [
        ProjectContext(
            name=record.name,
            description=record.description,
            start_date=record.start_date,
            end_date=record.end_date,
        )
        for record
        in student_profile.projects.order_by(
            "-start_date",
            "-id",
        )
    ]

    career_goals = [
        CareerGoalContext(
            target_role=record.target_role,
            description=record.description,
        )
        for record
        in student_profile.career_goals.order_by(
            "id",
        )
    ]

    return StudentProfileContext(
        skills=skills,
        education=education,
        experience=experience,
        projects=projects,
        career_goals=career_goals,
    )