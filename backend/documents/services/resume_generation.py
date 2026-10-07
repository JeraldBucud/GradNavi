"""
Resume-generation service foundation for GradNavi documents.

The caller must authenticate the Student and enforce profile ownership
before calling this service.
"""

from ai_services.prompts.resume import build_resume_prompt
from ai_services.providers.base import AIProvider
from ai_services.safety.privacy import build_student_profile_context
from ai_services.schemas.inputs import ResumeGenerationInput
from ai_services.schemas.outputs import (
    MAX_LIMITATION_ITEMS,
    ResumeDraft,
)
from profiles.models import StudentProfile


UNSUPPORTED_SKILL_LIMITATION = (
    "Unsupported generated skills were removed because they were "
    "not present in the Student Profile."
)


def _normalise_skill_value(value: str) -> str:
    """
    Normalise one skill label for deterministic comparison.
    """

    return " ".join(
        str(value).split()
    ).casefold()


def _build_supported_skill_lookup(
    *,
    student_profile: StudentProfile,
) -> dict[str, str]:
    """
    Map unambiguous Student Skill names and aliases to canonical names.

    Only skills owned by the authenticated Student Profile are eligible.
    Ambiguous aliases are intentionally excluded.
    """

    candidates: dict[
        str,
        set[str],
    ] = {}

    student_skills = (
        student_profile
        .student_skills
        .select_related(
            "skill",
        )
        .prefetch_related(
            "skill__aliases",
        )
        .order_by(
            "id",
        )
    )

    for student_skill in student_skills:
        canonical_name = (
            student_skill.skill.name.strip()
        )

        values = [
            canonical_name,
            *[
                alias.alias
                for alias
                in student_skill.skill.aliases.all()
            ],
        ]

        for value in values:
            key = _normalise_skill_value(
                value
            )

            if not key:
                continue

            candidates.setdefault(
                key,
                set(),
            ).add(
                canonical_name
            )

    return {
        key: next(
            iter(
                canonical_names
            )
        )
        for (
            key,
            canonical_names,
        )
        in candidates.items()
        if len(
            canonical_names
        ) == 1
    }


def _split_generated_skill_values(
    value: str,
) -> list[str]:
    """
    Split one generated skill line into individual candidate values.

    The approved prompt requests pipe-separated values. A conservative
    comma fallback keeps common provider formatting usable without
    weakening the Student Profile allowlist.
    """

    if "|" in value:
        parts = value.split("|")

    elif "," in value:
        parts = value.split(",")

    else:
        parts = [
            value,
        ]

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def _filter_resume_skills_to_profile(
    *,
    student_profile: StudentProfile,
    draft: ResumeDraft,
) -> ResumeDraft:
    """
    Remove generated skills that are not supported by the Student Profile.

    Provider output is structurally validated before reaching this point,
    but structural validation alone cannot prove that every generated skill
    came from the authenticated Student Profile. This deterministic allowlist
    closes that semantic-validation gap.
    """

    supported_lookup = (
        _build_supported_skill_lookup(
            student_profile=(
                student_profile
            ),
        )
    )

    filtered_lines = []
    unsupported_values = []
    seen_canonical = set()

    for raw_line in draft.skills:
        line = raw_line.strip()

        if not line:
            continue

        if ":" in line:
            category, values_text = (
                line.split(
                    ":",
                    1,
                )
            )

            category = category.strip()
            values_text = values_text.strip()

        else:
            category = ""
            values_text = line

        supported_values = []

        for generated_value in (
            _split_generated_skill_values(
                values_text
            )
        ):
            canonical_name = (
                supported_lookup.get(
                    _normalise_skill_value(
                        generated_value
                    )
                )
            )

            if canonical_name is None:
                unsupported_values.append(
                    generated_value
                )
                continue

            canonical_key = (
                _normalise_skill_value(
                    canonical_name
                )
            )

            if canonical_key in seen_canonical:
                continue

            seen_canonical.add(
                canonical_key
            )

            supported_values.append(
                canonical_name
            )

        if not supported_values:
            continue

        rendered_values = " | ".join(
            supported_values
        )

        if category:
            filtered_lines.append(
                f"{category}: {rendered_values}"
            )

        else:
            filtered_lines.append(
                rendered_values
            )

    if not unsupported_values:
        return draft

    limitations = list(
        draft.limitations
    )

    if (
        UNSUPPORTED_SKILL_LIMITATION
        not in limitations
        and len(limitations)
        < MAX_LIMITATION_ITEMS
    ):
        limitations.append(
            UNSUPPORTED_SKILL_LIMITATION
        )

    return draft.model_copy(
        update={
            "skills": filtered_lines,
            "limitations": limitations,
        }
    )


def generate_resume_draft(
    *,
    student_profile: StudentProfile,
    target_career_name: str,
    ai_provider: AIProvider,
    resume_focus: str = "balanced",
    target_job_title: str | None = None,
    job_description: str | None = None,
) -> ResumeDraft:
    """
    Generate a validated editable resume draft for an authorized profile.
    """

    profile_context = build_student_profile_context(
        student_profile=student_profile,
    )

    request = ResumeGenerationInput(
        profile=profile_context,
        target_career_name=target_career_name,
        target_job_title=target_job_title,
        resume_focus=resume_focus,
        job_description=job_description,
    )

    prompt_package = build_resume_prompt(
        request,
    )

    generated_draft = ai_provider.generate(
        prompt_package=prompt_package,
        output_model=ResumeDraft,
    )

    return _filter_resume_skills_to_profile(
        student_profile=student_profile,
        draft=generated_draft,
    )
