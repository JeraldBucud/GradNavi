from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from ai_services.exceptions import (
    AIProviderUnavailableError,
)
from ai_services.prompts.common import (
    AIOperation,
)
from ai_services.safety.privacy import (
    build_student_profile_context,
)
from ai_services.schemas.outputs import (
    LearningResourceGuidanceExplanation,
    LearningResourceGuidanceItem,
)
from careers.models import (
    Career,
    LearningResource,
    LearningResourceGuidanceSnapshot,
    LearningResourceSkill,
)
from careers.services.learning_resource_guidance import (
    LEARNING_RESOURCE_GUIDANCE_VERSION,
    MAX_AI_RESOURCES,
    build_learning_resource_guidance_cache_key,
    build_learning_resource_guidance_source,
    get_or_generate_learning_resource_guidance,
)
from careers.services.learning_resource_recommendations import (
    load_ranked_learning_resources,
)
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


class LearningResourceGuidanceServiceTests(
    TestCase
):

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "resource-guidance"
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


    def make_resources(
        self,
        count=8,
    ):
        resources = []

        for index in range(
            count
        ):
            resource = (
                LearningResource
                .objects
                .create(
                    resource_key=(
                        f"guidance-{index:02d}"
                    ),
                    title=(
                        f"Cloud Resource {index:02d}"
                    ),
                    provider=(
                        "GradNavi Test Provider"
                    ),
                    url=(
                        "https://example.com/"
                        f"guidance-{index:02d}"
                    ),
                    resource_type=(
                        LearningResource
                        .ResourceType
                        .COURSE
                    ),
                    description=(
                        "Controlled Cloud "
                        "Deployment resource."
                    ),
                    access_type=(
                        LearningResource
                        .AccessType
                        .FREE
                    ),
                    health_status=(
                        LearningResource
                        .HealthStatus
                        .ACTIVE
                    ),
                    is_active=True,
                )
            )

            LearningResourceSkill.objects.create(
                learning_resource=(
                    resource
                ),
                skill=self.skill,
            )

            resources.append(
                resource
            )

        return resources


    def ranked_resources(
        self,
    ):
        return (
            load_ranked_learning_resources(
                skill_id=self.skill.id,
                skill_name=self.skill.name,
                career_name=(
                    self.career.name
                ),
                limit=12,
            )
        )


    def provider(
        self,
        ranked,
    ):
        provider = Mock()

        provider.last_usage = {
            "input_tokens": 160,
            "output_tokens": 120,
            "total_tokens": 280,
        }

        provider.generate.return_value = (
            LearningResourceGuidanceExplanation(
                guidance_items=[
                    LearningResourceGuidanceItem(
                        resource_id=(
                            resource.id
                        ),
                        why_this_fits=(
                            f"{resource.title} fits "
                            "your current Cloud "
                            "Deployment development "
                            "focus."
                        ),
                    )
                    for resource
                    in ranked[
                        :MAX_AI_RESOURCES
                    ]
                ],
                is_ai_generated=True,
            )
        )

        return provider


    def test_source_limits_ai_to_first_six_resources(
        self,
    ):
        self.make_resources(
            count=8
        )

        ranked = (
            self.ranked_resources()
        )

        source = (
            build_learning_resource_guidance_source(
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                resources=ranked,
            )
        )

        self.assertEqual(
            len(
                source[
                    "resources"
                ]
            ),
            6,
        )

        self.assertEqual(
            MAX_AI_RESOURCES,
            6,
        )


    def test_prompt_uses_learning_resource_guidance_operation(
        self,
    ):
        from ai_services.prompts.learning_resource_guidance import (
            build_learning_resource_guidance_prompt,
        )

        self.make_resources(
            count=2
        )

        context = (
            build_student_profile_context(
                student_profile=(
                    self.profile
                )
            )
        )

        source = (
            build_learning_resource_guidance_source(
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                resources=(
                    self.ranked_resources()
                ),
            )
        )

        package = (
            build_learning_resource_guidance_prompt(
                profile=context,
                resource_context=source,
            )
        )

        self.assertEqual(
            package.operation,
            (
                AIOperation
                .LEARNING_RESOURCE_GUIDANCE
            ),
        )

        self.assertIn(
            "Cloud Deployment",
            package.trusted_context,
        )


    def test_first_request_generates_one_ai_batch_and_stores_cache(
        self,
    ):
        self.make_resources(
            count=8
        )

        ranked = (
            self.ranked_resources()
        )

        provider = self.provider(
            ranked
        )

        result = (
            get_or_generate_learning_resource_guidance(
                student_profile=(
                    self.profile
                ),
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                ranked_resources=(
                    ranked
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
            6,
        )

        self.assertEqual(
            result["version"],
            LEARNING_RESOURCE_GUIDANCE_VERSION,
        )

        provider.generate.assert_called_once()

        self.assertTrue(
            LearningResourceGuidanceSnapshot
            .objects
            .filter(
                student_profile=(
                    self.profile
                ),
                career=self.career,
                skill=self.skill,
            )
            .exists()
        )


    def test_second_request_uses_database_cache(
        self,
    ):
        self.make_resources(
            count=8
        )

        ranked = (
            self.ranked_resources()
        )

        provider = self.provider(
            ranked
        )

        first = (
            get_or_generate_learning_resource_guidance(
                student_profile=(
                    self.profile
                ),
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                ranked_resources=(
                    ranked
                ),
                provider=provider,
                model="gpt-test",
            )
        )

        second = (
            get_or_generate_learning_resource_guidance(
                student_profile=(
                    self.profile
                ),
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                ranked_resources=(
                    ranked
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


    def test_cache_changes_when_profile_evidence_changes(
        self,
    ):
        self.make_resources(
            count=2
        )

        ranked = (
            self.ranked_resources()
        )

        source = (
            build_learning_resource_guidance_source(
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                resources=ranked,
            )
        )

        first_context = (
            build_student_profile_context(
                student_profile=(
                    self.profile
                )
            )
        )

        first_key = (
            build_learning_resource_guidance_cache_key(
                profile_context=(
                    first_context
                ),
                source=source,
                model="gpt-test",
            )
        )

        student_skill = (
            StudentSkill.objects.get(
                student_profile=(
                    self.profile
                ),
                skill=self.skill,
            )
        )

        student_skill.proficiency_level = (
            StudentSkill
            .ProficiencyLevel
            .ADVANCED
        )

        student_skill.save(
            update_fields=[
                "proficiency_level",
                "updated_at",
            ]
        )

        second_context = (
            build_student_profile_context(
                student_profile=(
                    self.profile
                )
            )
        )

        second_key = (
            build_learning_resource_guidance_cache_key(
                profile_context=(
                    second_context
                ),
                source=source,
                model="gpt-test",
            )
        )

        self.assertNotEqual(
            first_key,
            second_key,
        )


    def test_cache_changes_when_selected_resources_change(
        self,
    ):
        self.make_resources(
            count=7
        )

        ranked = list(
            self.ranked_resources()
        )

        context = (
            build_student_profile_context(
                student_profile=(
                    self.profile
                )
            )
        )

        first_source = (
            build_learning_resource_guidance_source(
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                resources=ranked,
            )
        )

        changed_ranked = (
            ranked[1:]
            + ranked[:1]
        )

        second_source = (
            build_learning_resource_guidance_source(
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                resources=(
                    changed_ranked
                ),
            )
        )

        self.assertNotEqual(
            build_learning_resource_guidance_cache_key(
                profile_context=(
                    context
                ),
                source=first_source,
                model="gpt-test",
            ),
            build_learning_resource_guidance_cache_key(
                profile_context=(
                    context
                ),
                source=second_source,
                model="gpt-test",
            ),
        )


    def test_provider_failure_returns_deterministic_fallback(
        self,
    ):
        self.make_resources(
            count=8
        )

        ranked = (
            self.ranked_resources()
        )

        provider = Mock()

        provider.generate.side_effect = (
            AIProviderUnavailableError(
                "Provider unavailable."
            )
        )

        provider.last_usage = {}

        result = (
            get_or_generate_learning_resource_guidance(
                student_profile=(
                    self.profile
                ),
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                ranked_resources=(
                    ranked
                ),
                provider=provider,
                model="gpt-test",
            )
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
            6,
        )

        self.assertEqual(
            result[
                "guidance_items"
            ][0][
                "why_this_fits"
            ],
            ranked[0].why_this_fits,
        )

        self.assertFalse(
            LearningResourceGuidanceSnapshot
            .objects
            .filter(
                student_profile=(
                    self.profile
                ),
                career=self.career,
                skill=self.skill,
            )
            .exists()
        )


    def test_resources_seven_to_twelve_stay_outside_ai_batch(
        self,
    ):
        self.make_resources(
            count=12
        )

        ranked = (
            self.ranked_resources()
        )

        source = (
            build_learning_resource_guidance_source(
                career_id=(
                    self.career.id
                ),
                career_name=(
                    self.career.name
                ),
                skill_id=(
                    self.skill.id
                ),
                skill_name=(
                    self.skill.name
                ),
                resources=ranked,
            )
        )

        ai_ids = {
            item[
                "resource_id"
            ]
            for item
            in source[
                "resources"
            ]
        }

        deterministic_ids = {
            resource.id
            for resource
            in ranked[
                6:12
            ]
        }

        self.assertEqual(
            len(
                ai_ids
            ),
            6,
        )

        self.assertEqual(
            len(
                deterministic_ids
            ),
            6,
        )

        self.assertTrue(
            ai_ids.isdisjoint(
                deterministic_ids
            )
        )


    def test_snapshot_payload_does_not_store_raw_profile(
        self,
    ):
        self.make_resources(
            count=2
        )

        ranked = (
            self.ranked_resources()
        )

        provider = self.provider(
            ranked
        )

        get_or_generate_learning_resource_guidance(
            student_profile=(
                self.profile
            ),
            career_id=(
                self.career.id
            ),
            career_name=(
                self.career.name
            ),
            skill_id=(
                self.skill.id
            ),
            skill_name=(
                self.skill.name
            ),
            ranked_resources=(
                ranked
            ),
            provider=provider,
            model="gpt-test",
        )

        snapshot = (
            LearningResourceGuidanceSnapshot
            .objects
            .get(
                student_profile=(
                    self.profile
                ),
                career=self.career,
                skill=self.skill,
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


    def test_only_one_snapshot_is_kept_per_student_career_skill(
        self,
    ):
        self.make_resources(
            count=2
        )

        ranked = (
            self.ranked_resources()
        )

        first_provider = (
            self.provider(
                ranked
            )
        )

        get_or_generate_learning_resource_guidance(
            student_profile=(
                self.profile
            ),
            career_id=(
                self.career.id
            ),
            career_name=(
                self.career.name
            ),
            skill_id=(
                self.skill.id
            ),
            skill_name=(
                self.skill.name
            ),
            ranked_resources=(
                ranked
            ),
            provider=(
                first_provider
            ),
            model="gpt-test",
        )

        student_skill = (
            StudentSkill.objects.get(
                student_profile=(
                    self.profile
                ),
                skill=self.skill,
            )
        )

        student_skill.proficiency_level = (
            StudentSkill
            .ProficiencyLevel
            .ADVANCED
        )

        student_skill.save(
            update_fields=[
                "proficiency_level",
                "updated_at",
            ]
        )

        second_provider = (
            self.provider(
                ranked
            )
        )

        get_or_generate_learning_resource_guidance(
            student_profile=(
                self.profile
            ),
            career_id=(
                self.career.id
            ),
            career_name=(
                self.career.name
            ),
            skill_id=(
                self.skill.id
            ),
            skill_name=(
                self.skill.name
            ),
            ranked_resources=(
                ranked
            ),
            provider=(
                second_provider
            ),
            model="gpt-test",
        )

        self.assertEqual(
            LearningResourceGuidanceSnapshot
            .objects
            .filter(
                student_profile=(
                    self.profile
                ),
                career=self.career,
                skill=self.skill,
            )
            .count(),
            1,
        )
