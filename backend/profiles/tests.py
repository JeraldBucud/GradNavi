from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

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


def assert_error_envelope(test_case, response, code):
    test_case.assertIn("error", response.data)
    test_case.assertEqual(response.data["error"]["code"], code)
    test_case.assertIn("message", response.data["error"])
    test_case.assertIn("details", response.data["error"])


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


class StudentProfileReadAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/v1/profile/"
        self.password = "StrongPassword123!"
        self.user = User.objects.create_user(
            email="student-a@gradnavi.test",
            password=self.password,
            first_name="Student",
            last_name="A",
        )
        self.other_user = User.objects.create_user(
            email="student-b@gradnavi.test",
            password=self.password,
            first_name="Student",
            last_name="B",
        )
        self.profile = StudentProfile.objects.create(user=self.user)
        self.other_profile = StudentProfile.objects.create(user=self.other_user)
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.other_access_token = str(RefreshToken.for_user(self.other_user).access_token)

    def authenticated_get(self, token=None, path=None):
        return self.client.get(
            path or self.url,
            HTTP_AUTHORIZATION=f"Bearer {token or self.access_token}",
        )

    def test_route_resolves_to_profile_detail(self):
        self.assertEqual(resolve(self.url).url_name, "profile-detail")

    def test_authentication_is_required(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "not_authenticated")

    def test_invalid_authentication_uses_existing_error_envelope(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION="Bearer not-a-valid-token",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "token_not_valid")

    def test_authenticated_profile_get_returns_success_structure(self):
        response = self.authenticated_get()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {"data"})
        self.assertEqual(set(response.data["data"].keys()), {"profile"})
        self.assertEqual(
            set(response.data["data"]["profile"].keys()),
            {
                "skills",
                "interests",
                "education",
                "experience",
                "projects",
                "career_goals",
                "personality_responses",
            },
        )

    def test_complete_profile_sections_are_serialized(self):
        skill = Skill.objects.create(name="Python", category="Programming")
        interest = Interest.objects.create(name="Artificial Intelligence", category="Technology")
        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=StudentSkill.ProficiencyLevel.PROFICIENT,
        )
        StudentInterest.objects.create(student_profile=self.profile, interest=interest)
        Education.objects.create(
            student_profile=self.profile,
            institution_name="Central Queensland University",
            qualification="Master of Information Technology",
            field_of_study="Information Technology",
            start_date=date(2025, 3, 1),
            end_date=date(2026, 11, 30),
            description="Postgraduate study.",
        )
        Experience.objects.create(
            student_profile=self.profile,
            job_title="Junior Developer",
            company="GradNavi Labs",
            start_date=date(2025, 6, 1),
            is_current=True,
            description="Backend development.",
        )
        Project.objects.create(
            student_profile=self.profile,
            name="Career Planner",
            description="Student career-planning project.",
            project_url="https://example.com/project",
            start_date=date(2025, 7, 1),
        )
        CareerGoal.objects.create(
            student_profile=self.profile,
            target_role="Software Engineer",
            description="Build backend services.",
        )
        PersonalityResponse.objects.create(
            student_profile=self.profile,
            question_key="work_style",
            response_value="collaborative",
        )

        response = self.authenticated_get()
        profile = response.data["data"]["profile"]

        self.assertEqual(
            profile["skills"],
            [
                {
                    "id": skill.id,
                    "name": "Python",
                    "category": "Programming",
                    "proficiency_level": "proficient",
                }
            ],
        )
        self.assertEqual(
            profile["interests"],
            [{"id": interest.id, "name": "Artificial Intelligence", "category": "Technology"}],
        )
        self.assertEqual(
            profile["education"],
            [
                {
                    "id": self.profile.education.get().id,
                    "institution_name": "Central Queensland University",
                    "qualification": "Master of Information Technology",
                    "field_of_study": "Information Technology",
                    "start_date": "2025-03-01",
                    "end_date": "2026-11-30",
                    "description": "Postgraduate study.",
                }
            ],
        )
        self.assertEqual(profile["experience"][0]["job_title"], "Junior Developer")
        self.assertEqual(profile["experience"][0]["is_current"], True)
        self.assertEqual(profile["projects"][0]["name"], "Career Planner")
        self.assertEqual(profile["career_goals"][0]["target_role"], "Software Engineer")
        self.assertEqual(profile["personality_responses"][0]["question_key"], "work_style")
        self.assertNotIn("student_profile", str(profile))
        self.assertNotIn("user", str(profile))

    def test_empty_related_collections_are_returned(self):
        response = self.authenticated_get()

        self.assertEqual(
            response.data["data"]["profile"],
            {
                "skills": [],
                "interests": [],
                "education": [],
                "experience": [],
                "projects": [],
                "career_goals": [],
                "personality_responses": [],
            },
        )

    def test_get_uses_authenticated_user_and_does_not_leak_cross_user_data(self):
        own_skill = Skill.objects.create(name="Django", category="Backend")
        other_skill = Skill.objects.create(name="React", category="Frontend")
        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=own_skill,
            proficiency_level=StudentSkill.ProficiencyLevel.DEVELOPING,
        )
        StudentSkill.objects.create(
            student_profile=self.other_profile,
            skill=other_skill,
            proficiency_level=StudentSkill.ProficiencyLevel.ADVANCED,
        )
        CareerGoal.objects.create(
            student_profile=self.other_profile,
            target_role="Frontend Engineer",
        )

        response = self.authenticated_get(
            path=f"{self.url}?user_id={self.other_user.id}&profile_id={self.other_profile.id}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.data["data"]["profile"]
        self.assertEqual(profile["skills"][0]["name"], "Django")
        self.assertNotIn("React", str(profile))
        self.assertNotIn("Frontend Engineer", str(profile))

    def test_missing_student_profile_returns_not_found_without_creating_profile(self):
        self.profile.delete()

        response = self.authenticated_get()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        assert_error_envelope(self, response, "not_found")
        self.assertFalse(StudentProfile.objects.filter(user=self.user).exists())
