from django.contrib.auth import get_user_model
from django.test import TestCase

from careers.models import (
    Career,
    StudentCareerEvaluation,
)
from careers.services.explore_careers import (
    CareerEvaluationSnapshotUnavailableError,
    ExploreCareerNotAvailableError,
    evaluate_career_from_snapshot,
    get_valid_student_career_evaluation,
)
from careers.services.recommendation_cache import (
    build_recommendation_cache_key,
    store_recommendation_snapshot,
)
from profiles.models import (
    Skill,
    StudentProfile,
    StudentSkill,
)


class ExploreCareerEvaluationTests(
    TestCase
):
    def setUp(self):
        user_model = get_user_model()

        self.user = (
            user_model.objects.create_user(
                email=(
                    "explore-evaluation@"
                    "gradnavi.test"
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

        self.recommended_career = (
            Career.objects.create(
                name=(
                    "Explore Recommended Career"
                ),
                description=(
                    "Recommended test career."
                ),
                category="Technology",
                active=True,
            )
        )

        self.explore_career = (
            Career.objects.create(
                name=(
                    "Explore Explicit Career"
                ),
                description=(
                    "Explicit evaluation test career."
                ),
                category="Technology",
                active=True,
            )
        )

        self.inactive_career = (
            Career.objects.create(
                name=(
                    "Explore Inactive Career"
                ),
                description=(
                    "Inactive evaluation test career."
                ),
                category="Technology",
                active=False,
            )
        )

        self.cache_key = (
            build_recommendation_cache_key(
                student_profile=self.profile,
            )
        )

        self.snapshot = (
            store_recommendation_snapshot(
                student_profile=self.profile,
                payload={
                    "scoring_model": (
                        self.cache_key
                        .scoring_version
                    ),
                    "career_count": 2,
                    "recommendations": [
                        {
                            "career_id": (
                                self
                                .recommended_career
                                .id
                            ),
                            "career_name": (
                                self
                                .recommended_career
                                .name
                            ),
                            "recommendation_score": (
                                "88.50"
                            ),
                            "rank": 1,
                        },
                        {
                            "career_id": (
                                self
                                .explore_career
                                .id
                            ),
                            "career_name": (
                                self
                                .explore_career
                                .name
                            ),
                            "recommendation_score": (
                                "64.25"
                            ),
                            "rank": 2,
                        },
                    ],
                },
                embedding_model=(
                    "test-embedding-model"
                ),
                prompt_tokens=0,
                total_tokens=0,
                career_count=2,
                cache_key=self.cache_key,
            )
        )


    def test_explicit_evaluation_is_created(
        self,
    ):
        evaluation = (
            evaluate_career_from_snapshot(
                student_profile=self.profile,
                career_id=(
                    self.explore_career.id
                ),
            )
        )

        self.assertEqual(
            evaluation.student_profile_id,
            self.profile.id,
        )

        self.assertEqual(
            evaluation.career_id,
            self.explore_career.id,
        )

        self.assertEqual(
            evaluation.profile_fingerprint,
            (
                self.cache_key
                .profile_fingerprint
            ),
        )

        self.assertEqual(
            evaluation.reference_fingerprint,
            (
                self.cache_key
                .reference_fingerprint
            ),
        )

        self.assertEqual(
            evaluation.scoring_version,
            (
                self.cache_key
                .scoring_version
            ),
        )

        self.assertEqual(
            evaluation.payload[
                "career_id"
            ],
            self.explore_career.id,
        )

        self.assertEqual(
            evaluation.payload[
                "recommendation_score"
            ],
            "64.25",
        )

        self.assertEqual(
            StudentCareerEvaluation.objects.count(),
            1,
        )


    def test_explicit_evaluation_is_idempotent(
        self,
    ):
        first = (
            evaluate_career_from_snapshot(
                student_profile=self.profile,
                career_id=(
                    self.explore_career.id
                ),
            )
        )

        second = (
            evaluate_career_from_snapshot(
                student_profile=self.profile,
                career_id=(
                    self.explore_career.id
                ),
            )
        )

        self.assertEqual(
            first.id,
            second.id,
        )

        self.assertEqual(
            StudentCareerEvaluation.objects.count(),
            1,
        )


    def test_inactive_career_is_rejected(
        self,
    ):
        with self.assertRaises(
            ExploreCareerNotAvailableError
        ):
            evaluate_career_from_snapshot(
                student_profile=self.profile,
                career_id=(
                    self.inactive_career.id
                ),
            )

        self.assertEqual(
            StudentCareerEvaluation.objects.count(),
            0,
        )


    def test_missing_snapshot_is_rejected(
        self,
    ):
        self.snapshot.delete()

        with self.assertRaises(
            CareerEvaluationSnapshotUnavailableError
        ):
            evaluate_career_from_snapshot(
                student_profile=self.profile,
                career_id=(
                    self.explore_career.id
                ),
            )

        self.assertEqual(
            StudentCareerEvaluation.objects.count(),
            0,
        )


    def test_profile_change_makes_evaluation_stale(
        self,
    ):
        evaluation = (
            evaluate_career_from_snapshot(
                student_profile=self.profile,
                career_id=(
                    self.explore_career.id
                ),
            )
        )

        skill = Skill.objects.create(
            name=(
                "Explore Evaluation "
                "Fingerprint Skill"
            ),
            concept_type=(
                Skill.ConceptType.SKILL
            ),
        )

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=(
                StudentSkill
                .ProficiencyLevel
                .DEVELOPING
            ),
        )

        current = (
            get_valid_student_career_evaluation(
                student_profile=self.profile,
                career=self.explore_career,
            )
        )

        self.assertIsNone(
            current
        )

        self.assertTrue(
            StudentCareerEvaluation.objects.filter(
                id=evaluation.id
            ).exists()
        )


    def test_current_evaluation_is_returned(
        self,
    ):
        evaluation = (
            evaluate_career_from_snapshot(
                student_profile=self.profile,
                career_id=(
                    self.explore_career.id
                ),
            )
        )

        current = (
            get_valid_student_career_evaluation(
                student_profile=self.profile,
                career=self.explore_career,
            )
        )

        self.assertIsNotNone(
            current
        )

        self.assertEqual(
            current.id,
            evaluation.id,
        )
