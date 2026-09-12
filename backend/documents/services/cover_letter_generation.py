"""
Cover-letter generation service foundation for GradNavi documents.

The caller must authenticate the Student and enforce profile ownership
before calling this service.
"""

from ai_services.prompts.cover_letter import build_cover_letter_prompt
from ai_services.providers.base import AIProvider
from ai_services.safety.privacy import build_student_profile_context
from ai_services.schemas.inputs import CoverLetterGenerationInput
from ai_services.schemas.outputs import CoverLetterDraft
from profiles.models import StudentProfile


def generate_cover_letter_draft(
    *,
    student_profile: StudentProfile,
    job_description: str,
    ai_provider: AIProvider,
) -> CoverLetterDraft:
    """
    Generate a validated editable cover-letter draft for an authorized profile.
    """

    profile_context = build_student_profile_context(
        student_profile=student_profile,
    )

    request = CoverLetterGenerationInput(
        profile=profile_context,
        job_description=job_description,
    )

    prompt_package = build_cover_letter_prompt(
        request,
    )

    return ai_provider.generate(
        prompt_package=prompt_package,
        output_model=CoverLetterDraft,
    )

