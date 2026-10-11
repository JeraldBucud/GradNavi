from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from careers.models import (
    Career,
    CareerSkill,
    CareerSkillEvidence,
    ReferenceDataset,
    ReferenceSource,
    ReviewStatus,
    RoadmapProgress,
)
from careers.services.roadmap_overview import (
    build_roadmap_overview,
    generate_roadmap_overview,
)
from careers.services.learning_roadmap import (
    generate_learning_plan,
)
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


class RoadmapOverviewServiceTests(
    TestCase
):
    """
    Sprint 3 Career Roadmap overview integration tests.
    """

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "roadmap-overview"
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

        self.source = (
            ReferenceSource.objects.create(
                name="O*NET Database",
            )
        )

        self.dataset = (
            ReferenceDataset.objects.create(
                source=self.source,
                version=(
                    "roadmap-overview-v1"
                ),
                retrieved_at=date(
                    2026,
                    9,
                    18,
                ),
                status=(
                    ReferenceDataset
                    .Status
                    .ACTIVE
                ),
            )
        )

        self.career = (
            Career.objects.create(
                name=(
                    "Roadmap Overview Career"
                ),
                active=True,
            )
        )

        self.skill_one = (
            Skill.objects.create(
                name=(
                    "Roadmap Overview Skill One"
                ),
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )

        self.skill_two = (
            Skill.objects.create(
                name=(
                    "Roadmap Overview Skill Two"
                ),
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.skill_one,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .DEVELOPING
            ),
        )

        self._create_requirement(
            skill=self.skill_one,
            importance=Decimal(
                "90.00"
            ),
            required_level=Decimal(
                "80.00"
            ),
        )

        self._create_requirement(
            skill=self.skill_two,
            importance=Decimal(
                "70.00"
            ),
            required_level=Decimal(
                "60.00"
            ),
        )


    def _create_requirement(
        self,
        *,
        skill,
        importance,
        required_level,
    ):
        career_skill = (
            CareerSkill.objects.create(
                career=self.career,
                skill=skill,
                review_status=(
                    ReviewStatus
                    .APPROVED
                ),
            )
        )

        CareerSkillEvidence.objects.create(
            career_skill=career_skill,
            dataset=self.dataset,
            source_domain=(
                "onet_essential_skills"
            ),
            normalized_importance=(
                importance
            ),
            normalized_level=(
                required_level
            ),
            not_relevant=False,
        )

        return career_skill


    def test_overview_preserves_deterministic_roadmap_order(
        self,
    ):
        plan = generate_learning_plan(
            student_profile_id=(
                self.profile.id
            ),
            career_id=(
                self.career.id
            ),
        )

        overview = (
            build_roadmap_overview(
                plan=plan,
            )
        )

        self.assertEqual(
            [
                step.skill_id
                for step
                in overview.roadmap_steps
            ],
            [
                step.skill_id
                for step
                in plan.roadmap_steps
            ],
        )

        self.assertEqual(
            [
                step.step_number
                for step
                in overview.roadmap_steps
            ],
            [
                step.step_number
                for step
                in plan.roadmap_steps
            ],
        )


    def test_overview_preserves_readiness_result(
        self,
    ):
        plan = generate_learning_plan(
            student_profile_id=(
                self.profile.id
            ),
            career_id=(
                self.career.id
            ),
        )

        overview = (
            build_roadmap_overview(
                plan=plan,
            )
        )

        self.assertEqual(
            overview.career_id,
            plan.career_id,
        )

        self.assertEqual(
            overview.career_name,
            plan.career_name,
        )

        self.assertEqual(
            overview.score_status,
            (
                plan
                .readiness_result
                .score_status
            ),
        )

        self.assertEqual(
            overview.readiness_score,
            (
                plan
                .readiness_result
                .readiness_score
            ),
        )


    def test_missing_progress_rows_appear_as_not_started_without_writes(
        self,
    ):
        overview = (
            generate_roadmap_overview(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=(
                    self.career.id
                ),
            )
        )

        self.assertGreater(
            len(
                overview.roadmap_steps
            ),
            0,
        )

        self.assertTrue(
            all(
                step.progress_status
                == (
                    RoadmapProgress
                    .Status
                    .NOT_STARTED
                )
                for step
                in overview.roadmap_steps
            )
        )

        self.assertEqual(
            RoadmapProgress
            .objects
            .count(),
            0,
        )


    def test_existing_progress_is_attached_to_matching_skill(
        self,
    ):
        plan = generate_learning_plan(
            student_profile_id=(
                self.profile.id
            ),
            career_id=(
                self.career.id
            ),
        )

        target_step = (
            plan.roadmap_steps[0]
        )

        RoadmapProgress.objects.create(
            student_profile=self.profile,
            career=self.career,
            skill_id=(
                target_step.skill_id
            ),
            status=(
                RoadmapProgress
                .Status
                .IN_PROGRESS
            ),
        )

        overview = (
            build_roadmap_overview(
                plan=plan,
            )
        )

        matching_step = next(
            step
            for step
            in overview.roadmap_steps
            if step.skill_id
            == target_step.skill_id
        )

        self.assertEqual(
            matching_step.progress_status,
            (
                RoadmapProgress
                .Status
                .IN_PROGRESS
            ),
        )


    def test_progress_summary_counts_current_roadmap_only(
        self,
    ):
        plan = generate_learning_plan(
            student_profile_id=(
                self.profile.id
            ),
            career_id=(
                self.career.id
            ),
        )

        first_step = (
            plan.roadmap_steps[0]
        )

        RoadmapProgress.objects.create(
            student_profile=self.profile,
            career=self.career,
            skill_id=(
                first_step.skill_id
            ),
            status=(
                RoadmapProgress
                .Status
                .COMPLETED
            ),
        )

        stale_skill = (
            Skill.objects.create(
                name=(
                    "Roadmap Overview Stale Skill"
                ),
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )

        RoadmapProgress.objects.create(
            student_profile=self.profile,
            career=self.career,
            skill=stale_skill,
            status=(
                RoadmapProgress
                .Status
                .IN_PROGRESS
            ),
        )

        overview = (
            build_roadmap_overview(
                plan=plan,
            )
        )

        self.assertEqual(
            overview.progress_summary.total,
            len(
                plan.roadmap_steps
            ),
        )

        self.assertEqual(
            overview.progress_summary.completed,
            1,
        )

        self.assertEqual(
            overview.progress_summary.in_progress,
            0,
        )

        self.assertEqual(
            overview.progress_summary.not_started,
            (
                len(
                    plan.roadmap_steps
                )
                - 1
            ),
        )


    def test_progress_does_not_change_readiness(
        self,
    ):
        before = (
            generate_roadmap_overview(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=(
                    self.career.id
                ),
            )
        )

        first_step = (
            before.roadmap_steps[0]
        )

        RoadmapProgress.objects.create(
            student_profile=self.profile,
            career=self.career,
            skill_id=(
                first_step.skill_id
            ),
            status=(
                RoadmapProgress
                .Status
                .COMPLETED
            ),
        )

        after = (
            generate_roadmap_overview(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=(
                    self.career.id
                ),
            )
        )

        self.assertEqual(
            before.readiness_score,
            after.readiness_score,
        )

        self.assertEqual(
            [
                (
                    step.skill_id,
                    step.gap_amount,
                    step.required_level,
                )
                for step
                in before.roadmap_steps
            ],
            [
                (
                    step.skill_id,
                    step.gap_amount,
                    step.required_level,
                )
                for step
                in after.roadmap_steps
            ],
        )


    def test_student_skill_evidence_updates_readiness_independently_of_progress(
        self,
    ):
        before = (
            generate_roadmap_overview(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=(
                    self.career.id
                ),
            )
        )

        student_skill = (
            StudentSkill.objects.get(
                student_profile=self.profile,
                skill=self.skill_one,
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

        after = (
            generate_roadmap_overview(
                student_profile_id=(
                    self.profile.id
                ),
                career_id=(
                    self.career.id
                ),
            )
        )

        self.assertNotEqual(
            before.readiness_score,
            after.readiness_score,
        )

        self.assertEqual(
            RoadmapProgress
            .objects
            .count(),
            0,
        )
