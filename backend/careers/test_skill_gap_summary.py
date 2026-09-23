from decimal import Decimal
from unittest.mock import (
    Mock,
    patch,
)

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from ai_services.schemas.outputs import (
    SkillGapSummaryExplanation,
)
from careers.models import (
    Career,
    SkillGapSummarySnapshot,
)
from careers.services.learning_roadmap import (
    LearningPlan,
    LearningSuggestion,
)
from careers.services.readiness_scoring import (
    CareerReadinessResult,
    GapStatus,
    ReadinessStatus,
    SkillGapResult,
)
from profiles.models import StudentProfile


class SkillGapSummaryAPITests(
    APITestCase
):
    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model
            .objects
            .create_user(
                email=(
                    "skill-gap-summary@"
                    "gradnavi.test"
                ),
                password=(
                    "StrongPassword123!"
                ),
            )
        )

        self.profile = (
            StudentProfile
            .objects
            .create(
                user=self.user,
            )
        )

        self.career = (
            Career
            .objects
            .create(
                name=(
                    "Skill Gap Summary Career"
                )
            )
        )

        token = str(
            RefreshToken
            .for_user(
                self.user
            )
            .access_token
        )

        self.authorization = (
            f"Bearer {token}"
        )

        self.url = (
            "/api/v1/skill-gap-summary/"
            f"?career_id={self.career.id}"
        )


    def gap(
        self,
        *,
        skill_id,
        skill_name,
        status,
        proficiency=None,
        current_score=Decimal("0"),
        required_level=Decimal("70"),
        gap_amount=Decimal("70"),
        importance=Decimal("80"),
    ):
        return SkillGapResult(
            career_skill_id=(
                skill_id + 100
            ),
            skill_id=skill_id,
            skill_name=skill_name,
            concept_type="skill",
            source_domain=(
                "onet_essential_skills"
            ),
            student_proficiency_level=(
                proficiency
            ),
            student_proficiency_score=(
                current_score
            ),
            required_level=required_level,
            importance=importance,
            gap_amount=gap_amount,
            attainment_ratio=Decimal("0"),
            attainment_percentage=(
                Decimal("0")
            ),
            weighted_contribution=(
                Decimal("0")
            ),
            gap_status=status,
        )


    def plan(self):
        gaps = (
            self.gap(
                skill_id=1,
                skill_name="Deployment",
                status=GapStatus.MISSING,
            ),
            self.gap(
                skill_id=2,
                skill_name="Testing",
                status=(
                    GapStatus
                    .BELOW_REQUIREMENT
                ),
                proficiency="developing",
                current_score=Decimal("50"),
                required_level=Decimal("75"),
                gap_amount=Decimal("25"),
            ),
        )

        readiness = (
            CareerReadinessResult(
                career_id=self.career.id,
                career_name=self.career.name,
                score_status=(
                    ReadinessStatus.SCORED
                ),
                readiness_score=(
                    Decimal("42.00")
                ),
                matched_requirement_count=1,
                missing_requirement_count=1,
                below_requirement_count=1,
                meets_requirement_count=0,
                skill_gaps=gaps,
            )
        )

        suggestions = tuple(
            LearningSuggestion(
                priority=index,
                skill_id=gap.skill_id,
                skill_name=gap.skill_name,
                gap_status=gap.gap_status,
                current_proficiency=(
                    gap
                    .student_proficiency_level
                ),
                current_score=(
                    gap
                    .student_proficiency_score
                ),
                required_level=(
                    gap.required_level
                ),
                gap_amount=gap.gap_amount,
                importance=gap.importance,
                resources=(),
            )
            for index, gap
            in enumerate(
                gaps,
                start=1,
            )
        )

        return LearningPlan(
            student_profile_id=(
                self.profile.id
            ),
            career_id=(
                self.career.id
            ),
            career_name=(
                self.career.name
            ),
            readiness_result=readiness,
            suggestions=suggestions,
            roadmap_steps=(),
        )


    def get_summary(self):
        return self.client.get(
            self.url,
            HTTP_AUTHORIZATION=(
                self.authorization
            ),
        )


    def test_authentication_required(self):
        response = (
            self.client.get(
                self.url
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_first_request_generates_and_stores_cache(
        self,
    ):
        plan = self.plan()

        provider = Mock()

        provider.model = (
            "gpt-test"
        )

        provider.last_usage = {
            "input_tokens": 200,
            "output_tokens": 60,
            "total_tokens": 260,
        }

        provider.generate.return_value = (
            SkillGapSummaryExplanation(
                readiness_explanation=(
                    "Your readiness is limited by "
                    "missing deployment evidence and "
                    "testing that remains below the "
                    "required level."
                ),
                recommended_next_steps=[
                    "Add Deployment evidence from a concrete project.",
                    "Strengthen Testing evidence with a practical example.",
                ],
                is_ai_generated=True,
            )
        )

        with (
            patch(
                "careers.views."
                "generate_learning_plan",
                return_value=plan,
            ),
            patch(
                "careers.views."
                "resolve_text_model",
                return_value="gpt-test",
            ),
            patch(
                "careers.views."
                "OpenAITextProvider",
                return_value=provider,
            ) as provider_class,
        ):
            response = (
                self.get_summary()
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response
            .data["data"]
            ["cached"]
        )

        self.assertEqual(
            response
            .data["data"]
            ["fix_first"][0]
            ["skill_name"],
            "Deployment",
        )

        self.assertEqual(
            response
            .data["data"]
            ["usage"]
            ["total_tokens"],
            260,
        )

        provider_class.assert_called_once()

        self.assertTrue(
            SkillGapSummarySnapshot
            .objects
            .filter(
                student_profile=(
                    self.profile
                ),
                career=self.career,
            )
            .exists()
        )


    def test_second_request_uses_database_cache(
        self,
    ):
        plan = self.plan()

        provider = Mock()

        provider.model = "gpt-test"

        provider.last_usage = {
            "input_tokens": 200,
            "output_tokens": 60,
            "total_tokens": 260,
        }

        provider.generate.return_value = (
            SkillGapSummaryExplanation(
                readiness_explanation=(
                    "Cached readiness explanation."
                ),
                recommended_next_steps=[
                    "Address Deployment with stronger evidence.",
                    "Improve Testing with a concrete example.",
                ],
                is_ai_generated=True,
            )
        )

        with (
            patch(
                "careers.views."
                "generate_learning_plan",
                return_value=plan,
            ),
            patch(
                "careers.views."
                "resolve_text_model",
                return_value="gpt-test",
            ),
            patch(
                "careers.views."
                "OpenAITextProvider",
                return_value=provider,
            ) as provider_class,
        ):
            first = self.get_summary()

            second = self.get_summary()

        self.assertEqual(
            first.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            second.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            first.data["data"]["cached"]
        )

        self.assertTrue(
            second.data["data"]["cached"]
        )

        provider_class.assert_called_once()

        provider.generate.assert_called_once()


    def test_prompt_context_preserves_deterministic_fix_first_order(
        self,
    ):
        from careers.services.skill_gap_summary import (
            build_skill_gap_prompt_context,
            build_skill_gap_summary_source,
        )

        plan = self.plan()

        source = (
            build_skill_gap_summary_source(
                plan
            )
        )

        context = (
            build_skill_gap_prompt_context(
                source
            )
        )

        self.assertEqual(
            [
                item["skill_name"]
                for item
                in context["fix_first"]
            ],
            [
                "Deployment",
                "Testing",
            ],
        )

        self.assertEqual(
            [
                item["status"]
                for item
                in context["fix_first"]
            ],
            [
                "missing",
                "below_requirement",
            ],
        )


    def test_alignment_supports_two_fix_first_items(
        self,
    ):
        from careers.services.skill_gap_summary import (
            align_next_steps_to_fix_first,
        )

        result = (
            align_next_steps_to_fix_first(
                recommended_next_steps=[
                    (
                        "Improve Testing with "
                        "a concrete example."
                    ),
                    (
                        "Add Deployment evidence "
                        "from a project."
                    ),
                ],
                fix_first=[
                    {
                        "skill_name": "Deployment",
                    },
                    {
                        "skill_name": "Testing",
                    },
                ],
            )
        )

        self.assertEqual(
            result,
            [
                (
                    "Add Deployment evidence "
                    "from a project."
                ),
                (
                    "Improve Testing with "
                    "a concrete example."
                ),
            ],
        )


    def test_ai_actions_are_reordered_to_deterministic_fix_first(
        self,
    ):
        from careers.services.skill_gap_summary import (
            align_next_steps_to_fix_first,
        )

        result = (
            align_next_steps_to_fix_first(
                recommended_next_steps=[
                    (
                        "Address Deployment with a "
                        "concrete project example."
                    ),
                    (
                        "Improve Documentation with "
                        "clearer technical evidence."
                    ),
                    (
                        "Strengthen Testing using "
                        "a practical test example."
                    ),
                ],
                fix_first=[
                    {
                        "skill_name": "Deployment",
                    },
                    {
                        "skill_name": "Testing",
                    },
                    {
                        "skill_name": "Documentation",
                    },
                ],
            )
        )

        self.assertEqual(
            result,
            [
                (
                    "Address Deployment with a "
                    "concrete project example."
                ),
                (
                    "Strengthen Testing using "
                    "a practical test example."
                ),
                (
                    "Improve Documentation with "
                    "clearer technical evidence."
                ),
            ],
        )


    def test_cache_changes_when_readiness_changes(
        self,
    ):
        from careers.services.skill_gap_summary import (
            build_skill_gap_summary_cache_key,
            build_skill_gap_summary_source,
        )

        first_plan = self.plan()

        first_source = (
            build_skill_gap_summary_source(
                first_plan
            )
        )

        first_key = (
            build_skill_gap_summary_cache_key(
                first_source,
                model="gpt-test",
            )
        )

        changed_plan = self.plan()

        changed_plan = LearningPlan(
            student_profile_id=(
                changed_plan
                .student_profile_id
            ),
            career_id=(
                changed_plan.career_id
            ),
            career_name=(
                changed_plan.career_name
            ),
            readiness_result=(
                CareerReadinessResult(
                    career_id=(
                        self.career.id
                    ),
                    career_name=(
                        self.career.name
                    ),
                    score_status=(
                        ReadinessStatus.SCORED
                    ),
                    readiness_score=(
                        Decimal("60.00")
                    ),
                    matched_requirement_count=1,
                    missing_requirement_count=1,
                    below_requirement_count=1,
                    meets_requirement_count=0,
                    skill_gaps=(
                        changed_plan
                        .readiness_result
                        .skill_gaps
                    ),
                )
            ),
            suggestions=(
                changed_plan.suggestions
            ),
            roadmap_steps=(),
        )

        changed_source = (
            build_skill_gap_summary_source(
                changed_plan
            )
        )

        changed_key = (
            build_skill_gap_summary_cache_key(
                changed_source,
                model="gpt-test",
            )
        )

        self.assertNotEqual(
            first_key,
            changed_key,
        )
