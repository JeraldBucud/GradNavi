"""
Automated provider-contract tests for GradNavi WBS 6.2.

These tests verify the provider-independent AI boundary used by
Sprint 3 feature services.

No external AI provider is contacted.
"""

from pathlib import Path

from django.test import SimpleTestCase
from pydantic import ValidationError

from ai_services.exceptions import (
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    AIResponseValidationError,
    AIServiceError,
    AIUnsupportedOperationError,
)
from ai_services.prompts.common import (
    AIOperation,
    PromptPackage,
)
from ai_services.providers.base import AIProvider
from ai_services.schemas.outputs import ResumeDraft


def build_resume_prompt_package() -> PromptPackage:
    """
    Build one minimal valid provider-independent prompt package.
    """

    return PromptPackage(
        operation=AIOperation.RESUME_GENERATION,
        system_instructions=(),
        safety_rules=(),
        trusted_context="{}",
        untrusted_content="",
        output_requirements=(),
    )


class ValidStubProvider:
    """
    Test-only provider implementation.

    This class exists only inside the automated test suite.
    """

    def generate(
        self,
        *,
        prompt_package,
        output_model,
    ):
        data = {
            "professional_summary": "Example summary.",
            "skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "missing_information": [],
            "limitations": [],
            "is_draft": True,
            "requires_user_review": True,
        }

        return output_model.model_validate(data)


class InvalidOutputStubProvider:
    """
    Test-only provider returning malformed ResumeDraft data.
    """

    def generate(
        self,
        *,
        prompt_package,
        output_model,
    ):
        data = {
            "professional_summary": "Example summary.",
            "skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "missing_information": [],
            "limitations": [],
            "is_draft": False,
            "requires_user_review": True,
        }

        try:
            return output_model.model_validate(data)
        except ValidationError as exc:
            raise AIResponseValidationError(
                "Provider output failed GradNavi validation."
            ) from exc


class UnsupportedOperationStubProvider:
    """
    Test-only provider showing the shared unsupported-operation contract.
    """

    def generate(
        self,
        *,
        prompt_package,
        output_model,
    ):
        if prompt_package.operation != AIOperation.RESUME_GENERATION:
            raise AIUnsupportedOperationError(
                f"Unsupported operation: {prompt_package.operation}"
            )

        return ValidStubProvider().generate(
            prompt_package=prompt_package,
            output_model=output_model,
        )


class ProviderProtocolTests(SimpleTestCase):
    """
    Tests for the provider-independent AIProvider Protocol.
    """

    def test_valid_stub_satisfies_provider_protocol(self):
        provider = ValidStubProvider()

        self.assertIsInstance(
            provider,
            AIProvider,
        )

    def test_provider_returns_requested_output_model(self):
        provider = ValidStubProvider()

        result = provider.generate(
            prompt_package=build_resume_prompt_package(),
            output_model=ResumeDraft,
        )

        self.assertIsInstance(
            result,
            ResumeDraft,
        )

    def test_provider_output_keeps_required_draft_flags(self):
        provider = ValidStubProvider()

        result = provider.generate(
            prompt_package=build_resume_prompt_package(),
            output_model=ResumeDraft,
        )

        self.assertTrue(
            result.is_draft
        )

        self.assertTrue(
            result.requires_user_review
        )

    def test_invalid_provider_output_maps_to_validation_error(self):
        provider = InvalidOutputStubProvider()

        with self.assertRaises(
            AIResponseValidationError
        ):
            provider.generate(
                prompt_package=build_resume_prompt_package(),
                output_model=ResumeDraft,
            )

    def test_unsupported_operation_uses_controlled_exception(self):
        provider = UnsupportedOperationStubProvider()

        package = PromptPackage(
            operation=AIOperation.INTERVIEW_FEEDBACK,
            system_instructions=(),
            safety_rules=(),
            trusted_context="{}",
            untrusted_content="",
            output_requirements=(),
        )

        with self.assertRaises(
            AIUnsupportedOperationError
        ):
            provider.generate(
                prompt_package=package,
                output_model=ResumeDraft,
            )


class ProviderExceptionTests(SimpleTestCase):
    """
    Tests for provider-related GradNavi exception contracts.
    """

    def test_provider_error_inherits_from_service_error(self):
        self.assertTrue(
            issubclass(
                AIProviderError,
                AIServiceError,
            )
        )

    def test_provider_unavailable_error_inherits_from_provider_error(self):
        self.assertTrue(
            issubclass(
                AIProviderUnavailableError,
                AIProviderError,
            )
        )

    def test_provider_timeout_error_inherits_from_provider_error(self):
        self.assertTrue(
            issubclass(
                AIProviderTimeoutError,
                AIProviderError,
            )
        )

    def test_response_validation_error_inherits_from_provider_error(self):
        self.assertTrue(
            issubclass(
                AIResponseValidationError,
                AIProviderError,
            )
        )

    def test_unsupported_operation_error_inherits_from_service_error(self):
        self.assertTrue(
            issubclass(
                AIUnsupportedOperationError,
                AIServiceError,
            )
        )


class ProviderIndependenceTests(SimpleTestCase):
    """
    Tests confirming WBS 6.2 stays provider-independent.
    """

    def test_backend_requirements_do_not_include_openai_sdk(self):
        backend_directory = (
            Path(__file__).resolve().parents[2]
        )

        requirements_path = (
            backend_directory / "requirements.txt"
        )

        requirements = requirements_path.read_text(
            encoding="utf-8"
        ).lower()

        self.assertNotIn(
            "openai",
            requirements,
        )

    def test_provider_base_does_not_import_openai(self):
        provider_base_path = (
            Path(__file__).resolve().parents[1]
            / "providers"
            / "base.py"
        )

        source = provider_base_path.read_text(
            encoding="utf-8"
        ).lower()

        self.assertNotIn(
            "import openai",
            source,
        )

        self.assertNotIn(
            "from openai",
            source,
        )
    