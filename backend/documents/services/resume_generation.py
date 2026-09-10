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
    ai_provider: AIProvider,
) -> ResumeDraft:
    """
    Generate a validated editable resume draft for an authorized profile.
    """

    profile_context = build_student_profile_context(
        student_profile=student_profile,
    )

    request = ResumeGenerationInput(
        profile=profile_context,
    )

    prompt_package = build_resume_prompt(
        request,
    )

    return ai_provider.generate(
        prompt_package=prompt_package,
        output_model=ResumeDraft,
    )

