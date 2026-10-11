"""
Privacy-minimised semantic context for GradNavi AI Candidate A1.

Student data passes through the existing Sprint 4 privacy boundary first.
A1 then removes additional fields not required for Career Semantic Alignment.

Student semantic text excludes identity, account data, institution names,
company names, dates, project URLs, interests, personality responses,
database identifiers, timestamps, and authentication data.

Career semantic text uses approved active Career evidence only.
"""

from dataclasses import dataclass
from decimal import Decimal

from ai_services.exceptions import (
    AIInputError,
    AIMissingContextError,
)
from ai_services.safety.privacy import (
    build_student_profile_context,
)

from careers.models import (
    Career,
    CareerSkillEvidence,
    ReferenceDataset,
    ReviewStatus,
)
from careers.services.recommendation_scoring import (
    ONET_NUMERICAL_SOURCE_DOMAINS,
    ONET_SOURCE_NAME,
)

from profiles.models import StudentProfile


ESCO_SOURCE_NAME = "ESCO"

ONET_SOFTWARE_SOURCE_DOMAIN = (
    "onet_software_skills"
)


@dataclass(frozen=True)
class StudentSemanticContext:
    text: str

    skill_count: int
    education_count: int
    experience_count: int
    project_count: int
    career_goal_count: int


@dataclass(frozen=True)
class CareerNumericalSemanticEvidence:
    skill_name: str
    concept_type: str

    normalized_importance: Decimal
    normalized_level: Decimal


@dataclass(frozen=True)
class CareerTechnologySemanticEvidence:
    skill_name: str
    concept_type: str

    in_demand_percentage: Decimal


@dataclass(frozen=True)
class CareerEscoSemanticEvidence:
    skill_name: str
    concept_type: str
    relation: str


@dataclass(frozen=True)
class CareerSemanticEvidence:
    numerical: tuple[
        CareerNumericalSemanticEvidence,
        ...
    ]

    technologies: tuple[
        CareerTechnologySemanticEvidence,
        ...
    ]

    esco: tuple[
        CareerEscoSemanticEvidence,
        ...
    ]


@dataclass(frozen=True)
class CareerSemanticContext:
    text: str

    numerical_competency_count: int
    technology_count: int
    esco_relationship_count: int


def clean_semantic_text(
    value: str,
) -> str:
    """
    Collapse whitespace while preserving semantic content.
    """

    return " ".join(
        value.split()
    )


def format_decimal(
    value: Decimal,
) -> str:
    """
    Produce compact deterministic Decimal text.
    """

    formatted = format(
        value,
        "f",
    )

    if "." in formatted:
        formatted = (
            formatted
            .rstrip("0")
            .rstrip(".")
        )

    return (
        formatted
        if formatted
        else "0"
    )


def build_student_semantic_context(
    *,
    student_profile: StudentProfile,
) -> StudentSemanticContext:
    """
    Build privacy-minimised Student text for A1.
    """

    approved_context = (
        build_student_profile_context(
            student_profile=student_profile
        )
    )

    skills = sorted(
        approved_context.skills,
        key=lambda item: (
            item.name.casefold(),
            item.proficiency_level,
        ),
    )

    education = sorted(
        approved_context.education,
        key=lambda item: (
            item.qualification.casefold(),
            item.field_of_study.casefold(),
            item.description.casefold(),
        ),
    )

    experience = sorted(
        approved_context.experience,
        key=lambda item: (
            item.job_title.casefold(),
            item.description.casefold(),
        ),
    )

    projects = sorted(
        approved_context.projects,
        key=lambda item: (
            item.name.casefold(),
            item.description.casefold(),
        ),
    )

    career_goals = sorted(
        approved_context.career_goals,
        key=lambda item: (
            item.target_role.casefold(),
            item.description.casefold(),
        ),
    )

    sections = []

    if skills:
        lines = [
            "SKILLS",
        ]

        for item in skills:
            lines.append(
                "- "
                + clean_semantic_text(
                    item.name
                )
                + " | proficiency: "
                + item.proficiency_level
            )

        sections.append(
            "\n".join(
                lines
            )
        )

    if education:
        lines = [
            "EDUCATION",
        ]

        for item in education:
            line = (
                "- qualification: "
                + clean_semantic_text(
                    item.qualification
                )
                + " | field: "
                + clean_semantic_text(
                    item.field_of_study
                )
            )

            description = clean_semantic_text(
                item.description
            )

            if description:
                line += (
                    " | description: "
                    + description
                )

            lines.append(
                line
            )

        sections.append(
            "\n".join(
                lines
            )
        )

    if experience:
        lines = [
            "EXPERIENCE",
        ]

        for item in experience:
            line = (
                "- role: "
                + clean_semantic_text(
                    item.job_title
                )
            )

            description = clean_semantic_text(
                item.description
            )

            if description:
                line += (
                    " | description: "
                    + description
                )

            lines.append(
                line
            )

        sections.append(
            "\n".join(
                lines
            )
        )

    if projects:
        lines = [
            "PROJECTS",
        ]

        for item in projects:
            line = (
                "- project: "
                + clean_semantic_text(
                    item.name
                )
            )

            description = clean_semantic_text(
                item.description
            )

            if description:
                line += (
                    " | description: "
                    + description
                )

            lines.append(
                line
            )

        sections.append(
            "\n".join(
                lines
            )
        )

    if career_goals:
        lines = [
            "CAREER GOALS",
        ]

        for item in career_goals:
            line = (
                "- target role: "
                + clean_semantic_text(
                    item.target_role
                )
            )

            description = clean_semantic_text(
                item.description
            )

            if description:
                line += (
                    " | description: "
                    + description
                )

            lines.append(
                line
            )

        sections.append(
            "\n".join(
                lines
            )
        )

    if not sections:
        raise AIMissingContextError(
            "Student profile has no approved "
            "career-relevant semantic context."
        )

    text = (
        "STUDENT CAREER PROFILE\n\n"
        + "\n\n".join(
            sections
        )
    )

    return StudentSemanticContext(
        text=text,
        skill_count=len(
            skills
        ),
        education_count=len(
            education
        ),
        experience_count=len(
            experience
        ),
        project_count=len(
            projects
        ),
        career_goal_count=len(
            career_goals
        ),
    )


def load_career_semantic_evidence(
    *,
    career: Career,
) -> CareerSemanticEvidence:
    """
    Load approved active Career evidence for A1.
    """

    base_queryset = (
        CareerSkillEvidence.objects
        .select_related(
            "career_skill__skill",
            "dataset__source",
        )
        .filter(
            career_skill__career=career,
            career_skill__review_status=(
                ReviewStatus.APPROVED
            ),
            dataset__status=(
                ReferenceDataset.Status.ACTIVE
            ),
            not_relevant=False,
        )
        .exclude(
            recommend_suppress=True
        )
    )

    numerical_rows = (
        base_queryset
        .filter(
            dataset__source__name=(
                ONET_SOURCE_NAME
            ),
            source_domain__in=(
                ONET_NUMERICAL_SOURCE_DOMAINS
            ),
            normalized_importance__isnull=False,
            normalized_level__isnull=False,
        )
        .order_by(
            "-normalized_importance",
            "career_skill__skill__name",
            "career_skill__skill_id",
        )
    )

    technology_rows = (
        base_queryset
        .filter(
            dataset__source__name=(
                ONET_SOURCE_NAME
            ),
            source_domain=(
                ONET_SOFTWARE_SOURCE_DOMAIN
            ),
            in_demand=True,
            in_demand_percentage__isnull=False,
        )
        .order_by(
            "-in_demand_percentage",
            "career_skill__skill__name",
            "career_skill__skill_id",
        )
    )

    esco_rows = (
        base_queryset
        .filter(
            dataset__source__name=(
                ESCO_SOURCE_NAME
            ),
        )
        .order_by(
            "source_relation",
            "career_skill__skill__name",
            "career_skill__skill_id",
        )
    )

    numerical = tuple(
        CareerNumericalSemanticEvidence(
            skill_name=(
                row.career_skill.skill.name
            ),
            concept_type=(
                row.career_skill.skill.concept_type
            ),
            normalized_importance=(
                row.normalized_importance
            ),
            normalized_level=(
                row.normalized_level
            ),
        )
        for row in numerical_rows
    )

    technologies = tuple(
        CareerTechnologySemanticEvidence(
            skill_name=(
                row.career_skill.skill.name
            ),
            concept_type=(
                row.career_skill.skill.concept_type
            ),
            in_demand_percentage=(
                row.in_demand_percentage
            ),
        )
        for row in technology_rows
    )

    esco = tuple(
        CareerEscoSemanticEvidence(
            skill_name=(
                row.career_skill.skill.name
            ),
            concept_type=(
                row.career_skill.skill.concept_type
            ),
            relation=(
                clean_semantic_text(
                    row.source_relation
                    or "unspecified"
                )
            ),
        )
        for row in esco_rows
    )

    return CareerSemanticEvidence(
        numerical=numerical,
        technologies=technologies,
        esco=esco,
    )


def build_career_semantic_context(
    *,
    career: Career,
) -> CareerSemanticContext:
    """
    Build deterministic Career text for A1.
    """

    if not career.active:
        raise AIInputError(
            "Career semantic context requires "
            "an active Career."
        )

    evidence = (
        load_career_semantic_evidence(
            career=career
        )
    )

    sections = [
        "CAREER",
        "- name: "
        + clean_semantic_text(
            career.name
        ),
    ]

    category = clean_semantic_text(
        career.category
    )

    if category:
        sections.append(
            "- category: "
            + category
        )

    description = clean_semantic_text(
        career.description
    )

    if description:
        sections.append(
            "- description: "
            + description
        )

    blocks = [
        "\n".join(
            sections
        )
    ]

    if evidence.numerical:
        lines = [
            "O*NET NUMERICAL COMPETENCIES",
        ]

        for item in evidence.numerical:
            lines.append(
                "- "
                + clean_semantic_text(
                    item.skill_name
                )
                + " | type: "
                + clean_semantic_text(
                    item.concept_type
                )
                + " | importance: "
                + format_decimal(
                    item.normalized_importance
                )
                + " | level: "
                + format_decimal(
                    item.normalized_level
                )
            )

        blocks.append(
            "\n".join(
                lines
            )
        )

    if evidence.technologies:
        lines = [
            "O*NET IN-DEMAND TECHNOLOGIES",
        ]

        for item in evidence.technologies:
            lines.append(
                "- "
                + clean_semantic_text(
                    item.skill_name
                )
                + " | type: "
                + clean_semantic_text(
                    item.concept_type
                )
                + " | demand: "
                + format_decimal(
                    item.in_demand_percentage
                )
                + "%"
            )

        blocks.append(
            "\n".join(
                lines
            )
        )

    if evidence.esco:
        lines = [
            "ESCO SKILL RELATIONSHIPS",
        ]

        for item in evidence.esco:
            lines.append(
                "- "
                + clean_semantic_text(
                    item.skill_name
                )
                + " | type: "
                + clean_semantic_text(
                    item.concept_type
                )
                + " | relation: "
                + clean_semantic_text(
                    item.relation
                )
            )

        blocks.append(
            "\n".join(
                lines
            )
        )

    return CareerSemanticContext(
        text="\n\n".join(
            blocks
        ),
        numerical_competency_count=len(
            evidence.numerical
        ),
        technology_count=len(
            evidence.technologies
        ),
        esco_relationship_count=len(
            evidence.esco
        ),
    )
