from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from .models import (
    CareerGoal,
    Education,
    Experience,
    Interest,
    PersonalityResponse,
    Project,
    Skill,
    StudentInterest,
    StudentProfile,
    StudentSkill,
)


User = get_user_model()


class StudentProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="profile@gradnavi.test",
            password="StrongPassword123!",
            first_name="Profile",
            last_name="Student",
        )
        self.profile = StudentProfile.objects.create(user=self.user)

    def test_student_profile_has_one_to_one_user_relationship(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.user.student_profile, self.profile)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StudentProfile.objects.create(user=self.user)

    def test_student_owned_entities_associate_with_student_profile(self):
        education = Education.objects.create(
            student_profile=self.profile,
            institution_name="Central Queensland University",
            qualification="Master of Information Technology",
            field_of_study="Information Technology",
            start_date=date(2025, 3, 1),
        )
        experience = Experience.objects.create(
            student_profile=self.profile,
            job_title="Junior Developer",
            company="GradNavi Labs",
            start_date=date(2025, 6, 1),
            is_current=True,
        )
        project = Project.objects.create(
            student_profile=self.profile,
            name="Career Planner",
            description="A student career-planning project.",
            project_url="https://example.com/project",
            start_date=date(2025, 7, 1),
        )
        career_goal = CareerGoal.objects.create(
            student_profile=self.profile,
            target_role="Software Engineer",
        )
        response = PersonalityResponse.objects.create(
            student_profile=self.profile,
            question_key="work_style",
            response_value="collaborative",
        )

        self.assertEqual(list(self.profile.education.all()), [education])
        self.assertEqual(list(self.profile.experience.all()), [experience])
        self.assertEqual(list(self.profile.projects.all()), [project])
        self.assertEqual(list(self.profile.career_goals.all()), [career_goal])
        self.assertEqual(list(self.profile.personality_responses.all()), [response])

    def test_skill_is_shared_reference_entity(self):
        skill = Skill.objects.create(
            name="Python",
            category="Programming",
            description="General-purpose programming language.",
        )

        self.assertEqual(str(skill), "Python")
        self.assertEqual(skill.category, "Programming")

    def test_interest_is_shared_reference_entity(self):
        interest = Interest.objects.create(
            name="Artificial Intelligence",
            category="Technology",
        )

        self.assertEqual(str(interest), "Artificial Intelligence")
        self.assertEqual(interest.category, "Technology")

    def test_student_skill_relationship_links_profile_and_skill(self):
        skill = Skill.objects.create(name="Django", category="Backend")
        student_skill = StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=StudentSkill.ProficiencyLevel.PROFICIENT,
        )

        self.assertEqual(student_skill.student_profile, self.profile)
        self.assertEqual(student_skill.skill, skill)
        self.assertEqual(list(self.profile.student_skills.all()), [student_skill])
        self.assertEqual(list(skill.student_skills.all()), [student_skill])

    def test_student_interest_relationship_links_profile_and_interest(self):
        interest = Interest.objects.create(name="Cybersecurity", category="Technology")
        student_interest = StudentInterest.objects.create(
            student_profile=self.profile,
            interest=interest,
        )

        self.assertEqual(student_interest.student_profile, self.profile)
        self.assertEqual(student_interest.interest, interest)
        self.assertEqual(list(self.profile.student_interests.all()), [student_interest])
        self.assertEqual(list(interest.student_interests.all()), [student_interest])

    def test_duplicate_student_skill_for_same_profile_and_skill_is_rejected(self):
        skill = Skill.objects.create(name="React")
        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=StudentSkill.ProficiencyLevel.DEVELOPING,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StudentSkill.objects.create(
                    student_profile=self.profile,
                    skill=skill,
                    proficiency_level=StudentSkill.ProficiencyLevel.ADVANCED,
                )

    def test_duplicate_student_interest_for_same_profile_and_interest_is_rejected(self):
        interest = Interest.objects.create(name="Cloud Computing")
        StudentInterest.objects.create(student_profile=self.profile, interest=interest)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StudentInterest.objects.create(
                    student_profile=self.profile,
                    interest=interest,
                )

    def test_approved_proficiency_values_validate(self):
        skill = Skill.objects.create(name="PostgreSQL")

        for proficiency in StudentSkill.ProficiencyLevel.values:
            with self.subTest(proficiency=proficiency):
                student_skill = StudentSkill(
                    student_profile=self.profile,
                    skill=skill,
                    proficiency_level=proficiency,
                )
                student_skill.full_clean()

    def test_invalid_proficiency_is_rejected_by_model_validation_and_database(self):
        skill = Skill.objects.create(name="Java")
        student_skill = StudentSkill(
            student_profile=self.profile,
            skill=skill,
            proficiency_level="expert",
        )

        with self.assertRaises(ValidationError):
            student_skill.full_clean()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StudentSkill.objects.create(
                    student_profile=self.profile,
                    skill=skill,
                    proficiency_level="expert",
                )

    def test_student_owned_records_cascade_when_profile_is_deleted(self):
        Skill.objects.create(name="Communication")
        Education.objects.create(
            student_profile=self.profile,
            institution_name="Central Queensland University",
            qualification="Graduate Diploma",
            field_of_study="Information Technology",
            start_date=date(2025, 3, 1),
        )
        CareerGoal.objects.create(
            student_profile=self.profile,
            target_role="Business Analyst",
        )

        self.profile.delete()

        self.assertFalse(Education.objects.exists())
        self.assertFalse(CareerGoal.objects.exists())

    def test_shared_skill_and_interest_are_protected_while_in_use(self):
        skill = Skill.objects.create(name="Problem Solving")
        interest = Interest.objects.create(name="Data Analysis")
        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=StudentSkill.ProficiencyLevel.FOUNDATIONAL,
        )
        StudentInterest.objects.create(student_profile=self.profile, interest=interest)

        with self.assertRaises(ProtectedError):
            skill.delete()
        with self.assertRaises(ProtectedError):
            interest.delete()
