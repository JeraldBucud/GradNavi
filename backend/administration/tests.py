from django.contrib.auth import get_user_model
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from careers.models import Career, LearningResource
from profiles.models import Skill


User = get_user_model()


class AdministrationAPITestCase(APITestCase):
    def setUp(self):
        self.password = "GradNaviAdminTest123!"

        self.admin = User.objects.create_superuser(
            email="admin@gradnavi.test",
            password=self.password,
            first_name="Admin",
            last_name="User",
        )

        self.student = User.objects.create_user(
            email="student@gradnavi.test",
            password=self.password,
            first_name="Student",
            last_name="User",
        )

        self.admin_token = str(
            AccessToken.for_user(self.admin)
        )

        self.student_token = str(
            AccessToken.for_user(self.student)
        )

    def authenticate_admin(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {self.admin_token}"
            )
        )

    def authenticate_student(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {self.student_token}"
            )
        )


class AdministrationPermissionTests(
    AdministrationAPITestCase
):
    admin_urls = (
        "/api/v1/administration/users/",
        "/api/v1/administration/careers/",
        "/api/v1/administration/skills/",
        "/api/v1/administration/learning-resources/",
    )
    def test_non_admins_cannot_access_admin_detail_endpoints(
        self,
    ):
        career = Career.objects.create(
            name="Permission Test Career",
            description="Temporary permission test.",
            category="Testing",
            active=True,
        )

        skill = Skill.objects.create(
            name="Permission Test Skill",
            concept_type="skill",
            category="Testing",
            description="Temporary permission test.",
        )

        resource = LearningResource.objects.create(
            title="Permission Test Resource",
            resource_key="permission-test-resource",
            provider="GradNavi Test",
            url="https://example.com/permission-test",
            resource_type="tutorial",
            description="Temporary permission test.",
            is_active=True,
            access_type="free",
            source_type="curated",
            health_status="active",
        )

        detail_urls = (
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/"
            ),
            (
                "/api/v1/administration/careers/"
                f"{career.id}/"
            ),
            (
                "/api/v1/administration/skills/"
                f"{skill.id}/"
            ),
            (
                "/api/v1/administration/"
                "learning-resources/"
                f"{resource.id}/"
            ),
        )

        for url in detail_urls:
            with self.subTest(
                authentication="unauthenticated",
                url=url,
            ):
                self.client.credentials()
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )

            with self.subTest(
                authentication="student",
                url=url,
            ):
                self.authenticate_student()
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )
    def test_unauthenticated_users_cannot_access_admin_endpoints(
        self,
    ):
        for url in self.admin_urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )

    def test_students_cannot_access_admin_endpoints(
        self,
    ):
        self.authenticate_student()

        for url in self.admin_urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_403_FORBIDDEN,
                )

    def test_student_cannot_create_career(self):
        self.authenticate_student()

        response = self.client.post(
            "/api/v1/administration/careers/",
            {
                "name": "Unauthorized Career",
                "description": (
                    "Student must not create this."
                ),
                "category": "Testing",
                "active": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertFalse(
            Career.objects.filter(
                name="Unauthorized Career"
            ).exists()
        )

    def test_admin_can_access_all_admin_endpoints(self):
        self.authenticate_admin()

        for url in self.admin_urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )


class AdminUserManagementTests(
    AdministrationAPITestCase
):
    def test_admin_can_list_users_with_safe_fields(self):
        self.authenticate_admin()

        response = self.client.get(
            "/api/v1/administration/users/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        response_text = str(response.data)

        self.assertNotIn("password", response_text)
        self.assertNotIn(self.admin.password, response_text)
        self.assertNotIn(self.student.password, response_text)
        self.assertNotIn("is_superuser", response_text)
        self.assertNotIn("groups", response_text)
        self.assertNotIn("user_permissions", response_text)

    def test_admin_can_retrieve_user(self):
        self.authenticate_admin()

        response = self.client.get(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            self.student.id,
        )
        self.assertEqual(
            response.data["email"],
            self.student.email,
        )

    def test_admin_can_update_user(self):
        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/"
            ),
            {
                "first_name": "Updated",
                "last_name": "Student",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.student.refresh_from_db()

        self.assertEqual(
            self.student.first_name,
            "Updated",
        )


class AdminCareerManagementTests(
    AdministrationAPITestCase
):
    def test_admin_can_create_retrieve_update_and_delete_career(
        self,
    ):
        self.authenticate_admin()

        create_response = self.client.post(
            "/api/v1/administration/careers/",
            {
                "name": "Administration Test Career",
                "description": "Temporary test career.",
                "category": "Testing",
                "active": True,
            },
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        career_id = create_response.data["id"]

        retrieve_response = self.client.get(
            (
                "/api/v1/administration/careers/"
                f"{career_id}/"
            )
        )

        self.assertEqual(
            retrieve_response.status_code,
            status.HTTP_200_OK,
        )

        update_response = self.client.patch(
            (
                "/api/v1/administration/careers/"
                f"{career_id}/"
            ),
            {
                "category": "API Testing",
            },
            format="json",
        )

        self.assertEqual(
            update_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            update_response.data["category"],
            "API Testing",
        )

        delete_response = self.client.delete(
            (
                "/api/v1/administration/careers/"
                f"{career_id}/"
            )
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Career.objects.filter(
                id=career_id
            ).exists()
        )


class AdminSkillManagementTests(
    AdministrationAPITestCase
):
    def test_admin_can_create_retrieve_update_and_delete_skill(
        self,
    ):
        self.authenticate_admin()

        create_response = self.client.post(
            "/api/v1/administration/skills/",
            {
                "name": "Administration Test Skill",
                "concept_type": "skill",
                "category": "Testing",
                "description": "Temporary test skill.",
            },
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        skill_id = create_response.data["id"]

        retrieve_response = self.client.get(
            (
                "/api/v1/administration/skills/"
                f"{skill_id}/"
            )
        )

        self.assertEqual(
            retrieve_response.status_code,
            status.HTTP_200_OK,
        )

        update_response = self.client.patch(
            (
                "/api/v1/administration/skills/"
                f"{skill_id}/"
            ),
            {
                "category": "API Testing",
            },
            format="json",
        )

        self.assertEqual(
            update_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            update_response.data["category"],
            "API Testing",
        )

        delete_response = self.client.delete(
            (
                "/api/v1/administration/skills/"
                f"{skill_id}/"
            )
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Skill.objects.filter(
                id=skill_id
            ).exists()
        )


class AdminLearningResourceManagementTests(
    AdministrationAPITestCase
):
    def test_admin_can_assign_skills_to_learning_resource(
        self,
    ):
        self.authenticate_admin()

        skill = Skill.objects.create(
            name="Administration Resource Skill",
            concept_type="skill",
            category="Testing",
            description="Skill used for resource testing.",
        )

        response = self.client.post(
            "/api/v1/administration/learning-resources/",
            {
                "title": "Resource With Skill",
                "resource_key": "resource-with-skill",
                "provider": "GradNavi Test",
                "url": "https://example.com/resource-with-skill",
                "resource_type": "tutorial",
                "description": "Resource linked to a skill.",
                "is_active": True,
                "access_type": "free",
                "source_type": "curated",
                "health_status": "active",
                "skill_ids": [skill.id],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        resource = LearningResource.objects.get(
            id=response.data["id"]
        )

        self.assertTrue(
            resource.skills.filter(id=skill.id).exists()
        )
        self.assertEqual(
            response.data["skill_ids"],
            [skill.id],
        )
    def test_admin_can_create_retrieve_update_and_delete_resource(
        self,
    ):
        self.authenticate_admin()

        create_response = self.client.post(
            "/api/v1/administration/learning-resources/",
            {
                "title": "Administration Test Resource",
                "resource_key": "administration-test-resource",
                "provider": "GradNavi Test",
                "url": "https://example.com/resource",
                "resource_type": "tutorial",
                "description": "Temporary test resource.",
                "is_active": True,
                "access_type": "free",
                "source_type": "curated",
                "health_status": "active",
            },
            format="json",
        )

        self.assertEqual(
            create_response.status_code,
            status.HTTP_201_CREATED,
        )

        resource_id = create_response.data["id"]

        retrieve_response = self.client.get(
            (
                "/api/v1/administration/"
                "learning-resources/"
                f"{resource_id}/"
            )
        )

        self.assertEqual(
            retrieve_response.status_code,
            status.HTTP_200_OK,
        )

        update_response = self.client.patch(
            (
                "/api/v1/administration/"
                "learning-resources/"
                f"{resource_id}/"
            ),
            {
                "health_status": "needs_review",
            },
            format="json",
        )

        self.assertEqual(
            update_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            update_response.data["health_status"],
            "needs_review",
        )

        delete_response = self.client.delete(
            (
                "/api/v1/administration/"
                "learning-resources/"
                f"{resource_id}/"
            )
        )

        self.assertEqual(
            delete_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            LearningResource.objects.filter(
                id=resource_id
            ).exists()
        )


class AdministrationURLRoutingTests(APITestCase):
    def test_administration_routes_are_registered(self):
        expected_routes = {
            "/api/v1/administration/users/":
                "admin-user-list",
            "/api/v1/administration/careers/":
                "admin-career-list",
            "/api/v1/administration/skills/":
                "admin-skill-list",
            "/api/v1/administration/learning-resources/":
                "admin-learning-resource-list",
        }

        for path, expected_name in expected_routes.items():
            with self.subTest(path=path):
                self.assertEqual(
                    resolve(path).url_name,
                    expected_name,
                )