from django.contrib.auth import get_user_model
from django.db import (
    IntegrityError,
    transaction,
)
from django.test import TestCase

from careers.models import Career
from profiles.models import (
    CareerGoal,
    StudentProfile,
)


class CareerGoalReferenceModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            email="career-goal-test@example.com",
            password="test-password",
        )

        self.profile = StudentProfile.objects.create(
            user=self.user,
        )

        self.software = Career.objects.create(
            name="Career Goal Software",
            active=True,
        )

        self.data = Career.objects.create(
            name="Career Goal Data",
            active=True,
        )

    def test_career_goal_links_to_career(self):
        goal = CareerGoal.objects.create(
            student_profile=self.profile,
            career=self.software,
            target_role=self.software.name,
            is_primary=True,
        )

        self.assertEqual(
            goal.career,
            self.software,
        )

        self.assertTrue(
            goal.is_primary
        )

    def test_only_one_primary_goal_per_profile(self):
        CareerGoal.objects.create(
            student_profile=self.profile,
            career=self.software,
            target_role=self.software.name,
            is_primary=True,
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CareerGoal.objects.create(
                    student_profile=self.profile,
                    career=self.data,
                    target_role=self.data.name,
                    is_primary=True,
                )

    def test_same_career_cannot_be_added_twice(self):
        CareerGoal.objects.create(
            student_profile=self.profile,
            career=self.software,
            target_role=self.software.name,
        )

        with self.assertRaises(
            IntegrityError
        ):
            with transaction.atomic():
                CareerGoal.objects.create(
                    student_profile=self.profile,
                    career=self.software,
                    target_role=self.software.name,
                )

    def test_legacy_text_goal_still_supported(self):
        goal = CareerGoal.objects.create(
            student_profile=self.profile,
            target_role="Legacy Career Goal",
        )

        self.assertIsNone(
            goal.career
        )

        self.assertEqual(
            str(goal),
            "Legacy Career Goal",
        )

