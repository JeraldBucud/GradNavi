"""
Resume-generation service foundation for GradNavi documents.

The caller must authenticate the Student and enforce profile ownership
before calling this service.
"""

from ai_services.prompts.resume import build_resume_prompt
from ai_services.providers.base import AIProvider
from ai_services.safety.privacy import build_student_profile_context
from ai_services.schemas.inputs import ResumeGenerationInput
from ai_services.schemas.outputs import ResumeDraft
from profiles.models import StudentProfile


def generate_resume_draft(
    *,
    student_profile: StudentProfile,
    target_career_name: str,
    ai_provider: AIProvider,
    resume_focus: str = "balanced",
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
        resume_focus=resume_focus,
        job_description=job_description,
    )

    prompt_package = build_resume_prompt(
        request,
    )

    return ai_provider.generate(
        prompt_package=prompt_package,
        output_model=ResumeDraft,
    )
