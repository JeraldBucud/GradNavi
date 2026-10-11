from types import SimpleNamespace
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from ai_services.exceptions import (
    AIProviderUnavailableError,
)
from ai_services.prompts.common import (
    AIOperation,
)
from ai_services.schemas.outputs import (
    RoadmapGuidanceExplanation,
    RoadmapGuidanceItem,
)
from careers.models import (
    Career,
    RoadmapGuidanceSnapshot,
)
from careers.services.roadmap_guidance import (
    ROADMAP_GUIDANCE_VERSION,
    build_roadmap_guidance_cache_key,
    build_roadmap_guidance_source,
    get_or_generate_roadmap_guidance,
)
from ai_services.safety.privacy import (
    build_student_profile_context,
)
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


class RoadmapGuidanceServiceTests(
    TestCase
):

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "roadmap-guidance"
                    "@gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        self.profile = (
            StudentProfile.objects.create(
                user=self.user,
            )
        )

        self.career = (
            Career.objects.create(
                name="Software Engineer",
                active=True,
            )
        )

        self.skill = (
            Skill.objects.create(
                name="Cloud Deployment",
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.skill,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .DEVELOPING
            ),
        )


    def make_step(
        self,
        *,
        number,
        skill_id,
        skill_name,
        progress_status="not_started",
    ):
        return SimpleNamespace(
            step_number=number,
            skill_id=skill_id,
            skill_name=skill_name,
            gap_status=(
                "below_requirement"
            ),
            current_proficiency=(
                "developing"
            ),
            current_score=50,
            required_level=75,
            gap_amount=25,
            importance=80,
            resources=(),
            progress_status=(
                progress_status
            ),
            started_at=None,
            completed_at=None,
        )


    def overview(
        self,
        *,
        readiness_score=55,
        progress_status="not_started",
    ):
        return SimpleNamespace(
            student_profile_id=(
                self.profile.id
            ),
            career_id=(
                self.career.id
            ),
            career_name=(
                self.career.name
            ),
            score_status="scored",
            readiness_score=(
                readiness_score
            ),
            roadmap_steps=(
                self.make_step(
                    number=1,
                    skill_id=1,
                    skill_name=(
                        "Cloud Deployment"
                    ),
                    progress_status=(
                        progress_status
                    ),
                ),
                self.make_step(
                    number=2,
                    skill_id=2,
                    skill_name="Testing",
                ),
                self.make_step(
                    number=3,
                    skill_id=3,
                    skill_name=(
                        "Version Control"
                    ),
                ),
                self.make_step(
                    number=4,
                    skill_id=4,
                    skill_name=(
                        "Documentation"
                    ),
                ),
            ),
        )


    def provider(
        self,
    ):
        provider = Mock()

        provider.last_usage = {
            "input_tokens": 120,
            "output_tokens": 70,
            "total_tokens": 190,
        }

        provider.generate.return_value = (
            RoadmapGuidanceExplanation(
                guidance_items=[
                    RoadmapGuidanceItem(
                        skill_name=(
                            "Cloud Deployment"
                        ),
                        why_this_matters=(
                            "Your current profile shows "
                            "developing evidence in this "
                            "priority area."
                        ),
                        your_focus=(
                            "Strengthen practical Cloud "
                            "Deployment evidence."
                        ),
                    ),
                    RoadmapGuidanceItem(
                        skill_name="Testing",
                        why_this_matters=(
                            "Testing is one of your "
                            "current roadmap gaps."
                        ),
                        your_focus=(
                            "Build clearer testing evidence."
                        ),
                    ),
                    RoadmapGuidanceItem(
                        skill_name=(
                            "Version Control"
                        ),
                        why_this_matters=(
                            "Version Control is one of "
                            "your current roadmap gaps."
                        ),
                        your_focus=(
                            "Strengthen version-control "
                            "workflow evidence."
                        ),
                    ),
                ],
                is_ai_generated=True,
            )
        )

        return provider


    def test_source_limits_ai_to_top_three_steps(
        self,
    ):
        source = (
            build_roadmap_guidance_source(
                self.overview()
            )
        )

        self.assertEqual(
            [
                item["skill_name"]
                for item
                in source[
                    "roadmap_steps"
                ]
            ],
            [
                "Cloud Deployment",
                "Testing",
                "Version Control",
            ],
        )


    def test_prompt_uses_roadmap_guidance_operation(
        self,
    ):
        from ai_services.prompts.roadmap_guidance import (
            build_roadmap_guidance_prompt,
        )

        context = (
            build_student_profile_context(
                student_profile=(
                    self.profile
                )
            )
        )

        package = (
            build_roadmap_guidance_prompt(
                profile=context,
                roadmap_context=(
                    build_roadmap_guidance_source(
                        self.overview()
                    )
                ),
            )
        )

        self.assertEqual(
            package.operation,
            (
                AIOperation
                .ROADMAP_GUIDANCE
            ),
        )

        self.assertIn(
            "Cloud Deployment",
            package.trusted_context,
        )


    def test_first_request_generates_and_stores_snapshot(
        self,
    ):
        provider = self.provider()

        result = (
            get_or_generate_roadmap_guidance(
                student_profile=(
                    self.profile
                ),
                overview=(
                    self.overview()
                ),
                provider=provider,
                model="gpt-test",
            )
        )

        self.assertFalse(
            result["cached"]
        )

        self.assertFalse(
            result["fallback"]
        )

        self.assertTrue(
            result[
                "is_ai_generated"
            ]
        )

        self.assertEqual(
            len(
                result[
                    "guidance_items"
                ]
            ),
            3,
        )

        self.assertEqual(
            result["version"],
            ROADMAP_GUIDANCE_VERSION,
        )

        self.assertTrue(
            RoadmapGuidanceSnapshot
            .objects
            .filter(
                student_profile=(
                    self.profile
                ),
                career=self.career,
            )
            .exists()
        )

        provider.generate.assert_called_once()


    def test_second_request_uses_database_cache(
        self,
    ):
        provider = self.provider()

        first = (
            get_or_generate_roadmap_guidance(
                student_profile=(
                    self.profile
                ),
                overview=(
                    self.overview()
                ),
                provider=provider,
                model="gpt-test",
            )
        )

        second = (
            get_or_generate_roadmap_guidance(
                student_profile=(
                    self.profile
                ),
                overview=(
                    self.overview()
                ),
                provider=provider,
                model="gpt-test",
            )
        )

        self.assertFalse(
            first["cached"]
        )

        self.assertTrue(
            second["cached"]
        )

        provider.generate.assert_called_once()


    def test_cache_changes_when_relevant_roadmap_changes(
        self,
    ):
        context = (
            build_student_profile_context(
                student_profile=(
                    self.profile
                )
            )
        )

        first_source = (
            build_roadmap_guidance_source(
                self.overview(
                    readiness_score=55
                )
            )
        )

        second_source = (
            build_roadmap_guidance_source(
                self.overview(
                    readiness_score=70
                )
            )
        )

        first_key = (
            build_roadmap_guidance_cache_key(
                profile_context=context,
                roadmap_source=(
                    first_source
                ),
                model="gpt-test",
            )
        )

        second_key = (
            build_roadmap_guidance_cache_key(
                profile_context=context,
                roadmap_source=(
                    second_source
                ),
                model="gpt-test",
            )
        )

        self.assertNotEqual(
            first_key,
            second_key,
        )


    def test_cache_changes_when_progress_changes(
        self,
    ):
        context = (
            build_student_profile_context(
                student_profile=(
                    self.profile
                )
            )
        )

        first = (
            build_roadmap_guidance_source(
                self.overview(
                    progress_status=(
                        "not_started"
                    )
                )
            )
        )

        second = (
            build_roadmap_guidance_source(
                self.overview(
                    progress_status=(
                        "in_progress"
                    )
                )
            )
        )

        self.assertNotEqual(
            build_roadmap_guidance_cache_key(
                profile_context=context,
                roadmap_source=first,
                model="gpt-test",
            ),
            build_roadmap_guidance_cache_key(
                profile_context=context,
                roadmap_source=second,
                model="gpt-test",
            ),
        )


    def test_provider_failure_returns_fallback_without_cache(
        self,
    ):
        provider = Mock()

        provider.generate.side_effect = (
            AIProviderUnavailableError(
                "Provider unavailable."
            )
        )

        provider.last_usage = {}

        result = (
            get_or_generate_roadmap_guidance(
                student_profile=(
                    self.profile
                ),
                overview=(
                    self.overview()
                ),
                provider=provider,
                model="gpt-test",
            )
        )

        self.assertFalse(
            result["cached"]
        )

        self.assertTrue(
            result["fallback"]
        )

        self.assertFalse(
            result[
                "is_ai_generated"
            ]
        )

        self.assertEqual(
            len(
                result[
                    "guidance_items"
                ]
            ),
            3,
        )

        self.assertFalse(
            RoadmapGuidanceSnapshot
            .objects
            .filter(
                student_profile=(
                    self.profile
                ),
                career=self.career,
            )
            .exists()
        )


    def test_cached_payload_does_not_store_raw_profile(
        self,
    ):
        provider = self.provider()

        get_or_generate_roadmap_guidance(
            student_profile=(
                self.profile
            ),
            overview=(
                self.overview()
            ),
            provider=provider,
            model="gpt-test",
        )

        snapshot = (
            RoadmapGuidanceSnapshot
            .objects
            .get(
                student_profile=(
                    self.profile
                ),
                career=self.career,
            )
        )

        payload_text = str(
            snapshot.payload
        )

        self.assertNotIn(
            self.user.email,
            payload_text,
        )

        self.assertNotIn(
            "career_goals",
            payload_text,
        )


    def test_only_one_snapshot_is_kept_per_student_career(
        self,
    ):
        provider = self.provider()

        get_or_generate_roadmap_guidance(
            student_profile=(
                self.profile
            ),
            overview=(
                self.overview(
                    readiness_score=55
                )
            ),
            provider=provider,
            model="gpt-test",
        )

        provider_two = self.provider()

        get_or_generate_roadmap_guidance(
            student_profile=(
                self.profile
            ),
            overview=(
                self.overview(
                    readiness_score=70
                )
            ),
            provider=provider_two,
            model="gpt-test",
        )

        self.assertEqual(
            RoadmapGuidanceSnapshot
            .objects
            .filter(
                student_profile=(
                    self.profile
                ),
                career=self.career,
            )
            .count(),
            1,
        )
