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


class StudentProfilePatchAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/v1/profile/"
        self.password = "StrongPassword123!"
        self.user = User.objects.create_user(
            email="patch-a@gradnavi.test",
            password=self.password,
            first_name="Patch",
            last_name="A",
        )
        self.other_user = User.objects.create_user(
            email="patch-b@gradnavi.test",
            password=self.password,
            first_name="Patch",
            last_name="B",
        )
        self.profile = StudentProfile.objects.create(user=self.user)
        self.other_profile = StudentProfile.objects.create(user=self.other_user)
        self.access_token = str(RefreshToken.for_user(self.user).access_token)
        self.other_access_token = str(RefreshToken.for_user(self.other_user).access_token)

    def authenticated_patch(self, payload, token=None, path=None):
        return self.client.patch(
            path or self.url,
            payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {token or self.access_token}",
        )

    def authenticated_get(self):
        return self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

    def make_full_payload(self):
        skill = Skill.objects.create(name="Python", category="Programming")
        interest = Interest.objects.create(name="Artificial Intelligence", category="Technology")
        return {
            "skills": [
                {
                    "id": skill.id,
                    "proficiency_level": StudentSkill.ProficiencyLevel.PROFICIENT,
                }
            ],
            "interests": ["Artificial Intelligence"],
            "education": [
                {
                    "institution_name": "Central Queensland University",
                    "qualification": "Master of Information Technology",
                    "field_of_study": "Information Technology",
                    "start_date": "2025-03-01",
                    "end_date": "2026-11-30",
                    "description": "Postgraduate study.",
                }
            ],
            "experience": [
                {
                    "job_title": "Junior Developer",
                    "company": "GradNavi Labs",
                    "start_date": "2025-06-01",
                    "is_current": True,
                    "description": "Backend development.",
                }
            ],
            "projects": [
                {
                    "name": "Career Planner",
                    "description": "Student career-planning project.",
                    "project_url": "https://example.com/project",
                    "start_date": "2025-07-01",
                }
            ],
            "career_goals": ["Software Engineer"],
            "personality_responses": [
                {
                    "question_key": "work_style",
                    "response_value": "collaborative",
                }
            ],
            "_skill": skill,
            "_interest": interest,
        }

    def test_patch_requires_authentication(self):
        response = self.client.patch(self.url, {"career_goals": []}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "not_authenticated")

    def test_patch_returns_success_structure_and_persists_to_get(self):
        payload = self.make_full_payload()
        skill = payload.pop("_skill")
        interest = payload.pop("_interest")

        response = self.authenticated_patch(payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile = response.data["data"]["profile"]
        self.assertEqual(profile["skills"][0]["name"], skill.name)
        self.assertEqual(profile["skills"][0]["proficiency_level"], "proficient")
        self.assertEqual(profile["interests"][0]["name"], interest.name)
        self.assertEqual(profile["education"][0]["qualification"], "Master of Information Technology")
        self.assertEqual(profile["experience"][0]["job_title"], "Junior Developer")
        self.assertEqual(profile["projects"][0]["name"], "Career Planner")
        self.assertEqual(profile["career_goals"][0]["target_role"], "Software Engineer")
        self.assertEqual(profile["personality_responses"][0]["response_value"], "collaborative")

        get_response = self.authenticated_get()
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data, response.data)

    def test_omitted_sections_remain_unchanged(self):
        skill = Skill.objects.create(name="Django", category="Backend")
        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=skill,
            proficiency_level=StudentSkill.ProficiencyLevel.DEVELOPING,
        )
        Education.objects.create(
            student_profile=self.profile,
            institution_name="Existing University",
            qualification="Graduate Diploma",
            field_of_study="Information Technology",
            start_date=date(2024, 3, 1),
        )

        response = self.authenticated_patch({"career_goals": ["Software Engineer"]})
        profile = response.data["data"]["profile"]

        self.assertEqual(profile["career_goals"][0]["target_role"], "Software Engineer")
        self.assertEqual(profile["skills"][0]["name"], "Django")
        self.assertEqual(profile["education"][0]["institution_name"], "Existing University")

    def test_supplied_collections_replace_existing_values_and_empty_arrays_clear(self):
        old_skill = Skill.objects.create(name="Old Skill")
        new_skill = Skill.objects.create(name="New Skill")
        old_interest = Interest.objects.create(name="Old Interest")
        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=old_skill,
            proficiency_level=StudentSkill.ProficiencyLevel.FOUNDATIONAL,
        )
        StudentInterest.objects.create(student_profile=self.profile, interest=old_interest)
        CareerGoal.objects.create(student_profile=self.profile, target_role="Old Goal")

        response = self.authenticated_patch(
            {
                "skills": [
                    {
                        "name": "New Skill",
                        "proficiency_level": StudentSkill.ProficiencyLevel.ADVANCED,
                    }
                ],
                "interests": [],
                "career_goals": [],
            }
        )
        profile = response.data["data"]["profile"]

        self.assertEqual(profile["skills"][0]["name"], "New Skill")
        self.assertEqual(profile["skills"][0]["proficiency_level"], "advanced")
        self.assertEqual(profile["interests"], [])
        self.assertEqual(profile["career_goals"], [])
        self.assertFalse(self.profile.student_skills.filter(skill=old_skill).exists())
        self.assertFalse(self.profile.student_interests.exists())
        self.assertFalse(self.profile.career_goals.exists())

    def test_existing_nested_records_can_be_updated_by_owned_id(self):
        education = Education.objects.create(
            student_profile=self.profile,
            institution_name="Old University",
            qualification="Old Qualification",
            field_of_study="IT",
            start_date=date(2024, 1, 1),
        )
        experience = Experience.objects.create(
            student_profile=self.profile,
            job_title="Old Role",
            company="Old Company",
            start_date=date(2024, 2, 1),
        )
        project = Project.objects.create(
            student_profile=self.profile,
            name="Old Project",
            start_date=date(2024, 3, 1),
        )
        career_goal = CareerGoal.objects.create(
            student_profile=self.profile,
            target_role="Old Goal",
        )
        personality_response = PersonalityResponse.objects.create(
            student_profile=self.profile,
            question_key="old_key",
            response_value="old_value",
        )

        response = self.authenticated_patch(
            {
                "education": [
                    {
                        "id": education.id,
                        "institution_name": "New University",
                        "qualification": "New Qualification",
                        "field_of_study": "Software Engineering",
                        "start_date": "2025-01-01",
                    }
                ],
                "experience": [
                    {
                        "id": experience.id,
                        "job_title": "New Role",
                        "company": "New Company",
                        "start_date": "2025-02-01",
                        "is_current": False,
                    }
                ],
                "projects": [
                    {
                        "id": project.id,
                        "name": "New Project",
                        "description": "Updated project.",
                        "project_url": "",
                        "start_date": "2025-03-01",
                    }
                ],
                "career_goals": [
                    {
                        "id": career_goal.id,
                        "target_role": "New Goal",
                        "description": "Updated goal.",
                    }
                ],
                "personality_responses": [
                    {
                        "id": personality_response.id,
                        "question_key": "new_key",
                        "response_value": "new_value",
                    }
                ],
            }
        )
        profile = response.data["data"]["profile"]

        self.assertEqual(profile["education"][0]["institution_name"], "New University")
        self.assertEqual(profile["experience"][0]["job_title"], "New Role")
        self.assertEqual(profile["projects"][0]["name"], "New Project")
        self.assertEqual(profile["career_goals"][0]["target_role"], "New Goal")
        self.assertEqual(profile["personality_responses"][0]["question_key"], "new_key")

    def test_client_supplied_ownership_identifiers_are_rejected(self):
        response = self.authenticated_patch(
            {
                "user_id": self.other_user.id,
                "career_goals": ["Software Engineer"],
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error")
        self.assertFalse(self.profile.career_goals.exists())

    def test_cross_user_nested_id_is_rejected_without_modifying_other_profile(self):
        other_goal = CareerGoal.objects.create(
            student_profile=self.other_profile,
            target_role="Other Goal",
        )

        response = self.authenticated_patch(
            {
                "career_goals": [
                    {
                        "id": other_goal.id,
                        "target_role": "Hijacked Goal",
                    }
                ],
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error")
        other_goal.refresh_from_db()
        self.assertEqual(other_goal.target_role, "Other Goal")

    def test_duplicate_skill_and_interest_inputs_are_rejected(self):
        skill = Skill.objects.create(name="Python")
        interest = Interest.objects.create(name="Cybersecurity")

        skill_response = self.authenticated_patch(
            {
                "skills": [
                    {
                        "id": skill.id,
                        "proficiency_level": StudentSkill.ProficiencyLevel.DEVELOPING,
                    },
                    {
                        "name": "Python",
                        "proficiency_level": StudentSkill.ProficiencyLevel.ADVANCED,
                    },
                ]
            }
        )
        interest_response = self.authenticated_patch(
            {"interests": [{"id": interest.id}, {"name": "Cybersecurity"}]}
        )

        self.assertEqual(skill_response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, skill_response, "validation_error")
        self.assertEqual(interest_response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, interest_response, "validation_error")

    def test_invalid_proficiency_and_missing_reference_are_rejected(self):
        skill = Skill.objects.create(name="Java")

        invalid_proficiency = self.authenticated_patch(
            {"skills": [{"id": skill.id, "proficiency_level": "expert"}]}
        )
        missing_reference = self.authenticated_patch(
            {
                "interests": [
                    {
                        "id": 999999,
                    }
                ]
            }
        )

        self.assertEqual(invalid_proficiency.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, invalid_proficiency, "validation_error")
        self.assertEqual(missing_reference.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, missing_reference, "validation_error")

    def test_invalid_date_range_and_project_url_are_rejected(self):
        date_response = self.authenticated_patch(
            {
                "education": [
                    {
                        "institution_name": "Central Queensland University",
                        "qualification": "Graduate Diploma",
                        "field_of_study": "Information Technology",
                        "start_date": "2026-01-01",
                        "end_date": "2025-01-01",
                    }
                ]
            }
        )
        url_response = self.authenticated_patch(
            {
                "projects": [
                    {
                        "name": "Invalid URL Project",
                        "project_url": "not-a-url",
                        "start_date": "2025-01-01",
                    }
                ]
            }
        )

        self.assertEqual(date_response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, date_response, "validation_error")
        self.assertEqual(url_response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, url_response, "validation_error")

    def test_education_start_date_only_update_validates_existing_end_date(self):
        education = Education.objects.create(
            student_profile=self.profile,
            institution_name="Central Queensland University",
            qualification="Graduate Diploma",
            field_of_study="Information Technology",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        response = self.authenticated_patch(
            {"education": [{"id": education.id, "start_date": "2025-01-01"}]}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error")
        education.refresh_from_db()
        self.assertEqual(education.start_date, date(2024, 1, 1))
        self.assertEqual(education.end_date, date(2024, 12, 31))

    def test_education_end_date_only_update_validates_existing_start_date(self):
        education = Education.objects.create(
            student_profile=self.profile,
            institution_name="Central Queensland University",
            qualification="Graduate Diploma",
            field_of_study="Information Technology",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        response = self.authenticated_patch(
            {"education": [{"id": education.id, "end_date": "2023-12-31"}]}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error")
        education.refresh_from_db()
        self.assertEqual(education.start_date, date(2024, 1, 1))
        self.assertEqual(education.end_date, date(2024, 12, 31))

    def test_experience_partial_date_update_validates_effective_final_range(self):
        experience = Experience.objects.create(
            student_profile=self.profile,
            job_title="Developer",
            company="GradNavi Labs",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        response = self.authenticated_patch(
            {"experience": [{"id": experience.id, "start_date": "2025-01-01"}]}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error")
        experience.refresh_from_db()
        self.assertEqual(experience.start_date, date(2024, 1, 1))
        self.assertEqual(experience.end_date, date(2024, 12, 31))

    def test_project_partial_date_update_validates_effective_final_range(self):
        project = Project.objects.create(
            student_profile=self.profile,
            name="Career Planner",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        response = self.authenticated_patch(
            {"projects": [{"id": project.id, "end_date": "2023-12-31"}]}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error")
        project.refresh_from_db()
        self.assertEqual(project.start_date, date(2024, 1, 1))
        self.assertEqual(project.end_date, date(2024, 12, 31))

    def test_valid_partial_date_update_succeeds(self):
        education = Education.objects.create(
            student_profile=self.profile,
            institution_name="Central Queensland University",
            qualification="Graduate Diploma",
            field_of_study="Information Technology",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

        response = self.authenticated_patch(
            {"education": [{"id": education.id, "end_date": "2025-12-31"}]}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        education.refresh_from_db()
        self.assertEqual(education.start_date, date(2024, 1, 1))
        self.assertEqual(education.end_date, date(2025, 12, 31))

    def test_failed_nested_validation_does_not_partially_modify_profile(self):
        CareerGoal.objects.create(student_profile=self.profile, target_role="Existing Goal")

        response = self.authenticated_patch(
            {
                "career_goals": ["New Goal"],
                "projects": [
                    {
                        "name": "Invalid URL Project",
                        "project_url": "not-a-url",
                        "start_date": "2025-01-01",
                    }
                ],
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error")
        self.assertEqual(
            list(self.profile.career_goals.values_list("target_role", flat=True)),
            ["Existing Goal"],
        )
        self.assertFalse(self.profile.projects.exists())

    def test_missing_student_profile_patch_returns_not_found_without_creating_profile(self):
        self.profile.delete()

        response = self.authenticated_patch({"career_goals": ["Software Engineer"]})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        assert_error_envelope(self, response, "not_found")
        self.assertFalse(StudentProfile.objects.filter(user=self.user).exists())

    def test_authenticated_user_cannot_patch_another_profile_with_query_parameters(self):
        CareerGoal.objects.create(student_profile=self.other_profile, target_role="Other Goal")

        response = self.authenticated_patch(
            {"career_goals": ["Own Goal"]},
            path=f"{self.url}?user_id={self.other_user.id}&profile_id={self.other_profile.id}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            list(self.profile.career_goals.values_list("target_role", flat=True)),
            ["Own Goal"],
        )
        self.assertEqual(
            list(self.other_profile.career_goals.values_list("target_role", flat=True)),
            ["Other Goal"],
        )
