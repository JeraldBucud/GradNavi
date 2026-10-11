from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import TestCase

from careers.models import (
    Career,
    RoadmapProgress,
)
from careers.services.roadmap_progress import (
    RoadmapProgressTransitionError,
    RoadmapStepNotFoundError,
    complete_roadmap_step,
    reconcile_roadmap_progress,
    start_roadmap_step,
)
from profiles.models import (
    Skill,
    StudentProfile,
)


class RoadmapProgressServiceTests(
    TestCase
):
    """
    Sprint 3 Career Roadmap progress service tests.
    """

    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "roadmap-progress"
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
                name=(
                    "Roadmap Progress Career"
                ),
                active=True,
            )
        )

        self.skill_one = (
            Skill.objects.create(
                name=(
                    "Roadmap Progress Skill One"
                ),
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )

        self.skill_two = (
            Skill.objects.create(
                name=(
                    "Roadmap Progress Skill Two"
                ),
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )

        self.stale_skill = (
            Skill.objects.create(
                name=(
                    "Roadmap Progress Stale Skill"
                ),
                concept_type=(
                    Skill.ConceptType.SKILL
                ),
            )
        )


    def make_step(
        self,
        *,
        step_number,
        skill,
    ):
        return SimpleNamespace(
            step_number=step_number,
            skill_id=skill.id,
        )


    def make_plan(
        self,
        *,
        steps=None,
    ):
        if steps is None:
            steps = (
                self.make_step(
                    step_number=1,
                    skill=self.skill_one,
                ),
                self.make_step(
                    step_number=2,
                    skill=self.skill_two,
                ),
            )

        return SimpleNamespace(
            student_profile_id=(
                self.profile.id
            ),
            career_id=(
                self.career.id
            ),
            roadmap_steps=tuple(
                steps
            ),
        )


    def test_missing_rows_are_not_started_without_database_writes(
        self,
    ):
        snapshot = (
            reconcile_roadmap_progress(
                plan=self.make_plan(),
            )
        )

        self.assertEqual(
            [
                step.status
                for step
                in snapshot.steps
            ],
            [
                (
                    RoadmapProgress
                    .Status
                    .NOT_STARTED
                ),
                (
                    RoadmapProgress
                    .Status
                    .NOT_STARTED
                ),
            ],
        )

        self.assertEqual(
            snapshot.summary.total,
            2,
        )

        self.assertEqual(
            snapshot.summary.completed,
            0,
        )

        self.assertEqual(
            snapshot.summary.in_progress,
            0,
        )

        self.assertEqual(
            snapshot.summary.not_started,
            2,
        )

        self.assertEqual(
            RoadmapProgress
            .objects
            .count(),
            0,
        )


    def test_start_creates_in_progress_record(
        self,
    ):
        state = start_roadmap_step(
            plan=self.make_plan(),
            skill_id=self.skill_one.id,
        )

        self.assertEqual(
            state.status,
            (
                RoadmapProgress
                .Status
                .IN_PROGRESS
            ),
        )

        record = (
            RoadmapProgress
            .objects
            .get(
                student_profile=(
                    self.profile
                ),
                career=self.career,
                skill=self.skill_one,
            )
        )

        self.assertIsNotNone(
            record.started_at
        )

        self.assertIsNone(
            record.completed_at
        )


    def test_start_is_idempotent(
        self,
    ):
        first = start_roadmap_step(
            plan=self.make_plan(),
            skill_id=self.skill_one.id,
        )

        second = start_roadmap_step(
            plan=self.make_plan(),
            skill_id=self.skill_one.id,
        )

        self.assertEqual(
            first.status,
            second.status,
        )

        self.assertEqual(
            first.started_at,
            second.started_at,
        )

        self.assertEqual(
            RoadmapProgress
            .objects
            .count(),
            1,
        )


    def test_complete_preserves_existing_started_timestamp(
        self,
    ):
        started = start_roadmap_step(
            plan=self.make_plan(),
            skill_id=self.skill_one.id,
        )

        completed = (
            complete_roadmap_step(
                plan=self.make_plan(),
                skill_id=(
                    self.skill_one.id
                ),
            )
        )

        self.assertEqual(
            completed.status,
            (
                RoadmapProgress
                .Status
                .COMPLETED
            ),
        )

        self.assertEqual(
            completed.started_at,
            started.started_at,
        )

        self.assertIsNotNone(
            completed.completed_at
        )


    def test_direct_completion_sets_both_timestamps(
        self,
    ):
        completed = (
            complete_roadmap_step(
                plan=self.make_plan(),
                skill_id=(
                    self.skill_two.id
                ),
            )
        )

        self.assertEqual(
            completed.status,
            (
                RoadmapProgress
                .Status
                .COMPLETED
            ),
        )

        self.assertIsNotNone(
            completed.started_at
        )

        self.assertIsNotNone(
            completed.completed_at
        )


    def test_completion_is_idempotent(
        self,
    ):
        first = complete_roadmap_step(
            plan=self.make_plan(),
            skill_id=self.skill_one.id,
        )

        second = complete_roadmap_step(
            plan=self.make_plan(),
            skill_id=self.skill_one.id,
        )

        self.assertEqual(
            first.completed_at,
            second.completed_at,
        )

        self.assertEqual(
            RoadmapProgress
            .objects
            .count(),
            1,
        )


    def test_completed_step_is_not_silently_restarted(
        self,
    ):
        complete_roadmap_step(
            plan=self.make_plan(),
            skill_id=self.skill_one.id,
        )

        with self.assertRaises(
            RoadmapProgressTransitionError
        ):
            start_roadmap_step(
                plan=self.make_plan(),
                skill_id=(
                    self.skill_one.id
                ),
            )


    def test_skill_must_belong_to_current_roadmap(
        self,
    ):
        with self.assertRaises(
            RoadmapStepNotFoundError
        ):
            start_roadmap_step(
                plan=self.make_plan(),
                skill_id=(
                    self.stale_skill.id
                ),
            )

        with self.assertRaises(
            RoadmapStepNotFoundError
        ):
            complete_roadmap_step(
                plan=self.make_plan(),
                skill_id=(
                    self.stale_skill.id
                ),
            )


    def test_reconciliation_follows_skill_not_old_step_number(
        self,
    ):
        RoadmapProgress.objects.create(
            student_profile=self.profile,
            career=self.career,
            skill=self.skill_one,
            status=(
                RoadmapProgress
                .Status
                .COMPLETED
            ),
        )

        RoadmapProgress.objects.create(
            student_profile=self.profile,
            career=self.career,
            skill=self.stale_skill,
            status=(
                RoadmapProgress
                .Status
                .IN_PROGRESS
            ),
        )

        reordered_plan = self.make_plan(
            steps=(
                self.make_step(
                    step_number=1,
                    skill=self.skill_two,
                ),
                self.make_step(
                    step_number=2,
                    skill=self.skill_one,
                ),
            )
        )

        snapshot = (
            reconcile_roadmap_progress(
                plan=reordered_plan,
            )
        )

        self.assertEqual(
            [
                (
                    step.step_number,
                    step.skill_id,
                    step.status,
                )
                for step
                in snapshot.steps
            ],
            [
                (
                    1,
                    self.skill_two.id,
                    (
                        RoadmapProgress
                        .Status
                        .NOT_STARTED
                    ),
                ),
                (
                    2,
                    self.skill_one.id,
                    (
                        RoadmapProgress
                        .Status
                        .COMPLETED
                    ),
                ),
            ],
        )

        self.assertEqual(
            snapshot.summary.total,
            2,
        )

        self.assertEqual(
            snapshot.summary.completed,
            1,
        )

        self.assertEqual(
            snapshot.summary.in_progress,
            0,
        )

        self.assertEqual(
            snapshot.summary.not_started,
            1,
        )

        self.assertEqual(
            RoadmapProgress
            .objects
            .count(),
            2,
        )
