from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from administration.models import AuditRecord
from careers.models import (
    Career,
    CareerSkill,
    CareerSkillEvidence,
    LearningResource,
    LearningResourceReport,
    ReferenceDataset,
    ReferenceSource,
    ReviewStatus,
)
from profiles.models import (
    CareerGoal,
    Skill,
    StudentProfile,
    StudentSkill,
)


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
        "/api/v1/administration/analytics/",
        "/api/v1/administration/audit-records/",
        "/api/v1/administration/users/",
        "/api/v1/administration/careers/",
        "/api/v1/administration/skills/",
        "/api/v1/administration/learning-resources/",
        "/api/v1/administration/learning-resource-reports/",
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
        audit_record = AuditRecord.objects.create(
            actor=self.admin,
            action="admin.permission.test",
            area="careers",
            target_type="Career",
            target_id=str(career.id),
            metadata={},
        )

        detail_urls = (
            (
                "/api/v1/administration/audit-records/"
                f"{audit_record.id}/"
            ),
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

    def test_admin_cannot_change_role_or_active_status(self):
        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.admin.id}/"
            ),
            {
                "role": User.Role.STUDENT,
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.admin.refresh_from_db()

        self.assertEqual(
            self.admin.role,
            User.Role.ADMIN,
        )
        self.assertTrue(self.admin.is_active)

        self.assertEqual(
            response.data["role"],
            User.Role.ADMIN,
        )
        self.assertTrue(response.data["is_active"])


class AdminUserRoleStatusAuditTests(
    AdministrationAPITestCase
):
    def test_admin_can_change_user_role_through_dedicated_endpoint(
        self,
    ):
        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/role/"
            ),
            {
                "role": User.Role.ADMIN,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.student.refresh_from_db()

        self.assertEqual(
            self.student.role,
            User.Role.ADMIN,
        )
        self.assertTrue(
            AuditRecord.objects.filter(
                action="admin.user.role_changed",
                area="users",
                target_type="User",
                target_id=str(self.student.id),
                actor=self.admin,
                metadata={
                    "previous_role": User.Role.STUDENT,
                    "new_role": User.Role.ADMIN,
                },
            ).exists()
        )

    def test_admin_can_change_user_active_status_through_dedicated_endpoint(
        self,
    ):
        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/status/"
            ),
            {
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.student.refresh_from_db()

        self.assertFalse(self.student.is_active)
        self.assertTrue(
            AuditRecord.objects.filter(
                action="admin.user.status_changed",
                area="users",
                target_type="User",
                target_id=str(self.student.id),
                actor=self.admin,
                metadata={
                    "previous_is_active": True,
                    "new_is_active": False,
                },
            ).exists()
        )

    def test_invalid_role_change_is_rejected(self):
        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/role/"
            ),
            {
                "role": "owner",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertFalse(
            AuditRecord.objects.filter(
                action="admin.user.role_changed",
            ).exists()
        )

    def test_student_cannot_change_role_or_status(self):
        self.authenticate_student()

        role_response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/role/"
            ),
            {
                "role": User.Role.ADMIN,
            },
            format="json",
        )
        status_response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/status/"
            ),
            {
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            role_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            status_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_change_role_or_status(
        self,
    ):
        role_response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/role/"
            ),
            {
                "role": User.Role.ADMIN,
            },
            format="json",
        )
        status_response = self.client.patch(
            (
                "/api/v1/administration/users/"
                f"{self.student.id}/status/"
            ),
            {
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            role_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            status_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
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


class AdminLearningResourceReportReviewTests(
    AdministrationAPITestCase
):
    def setUp(self):
        super().setUp()

        self.student_profile = (
            StudentProfile.objects.create(
                user=self.student,
            )
        )

        self.learning_resource = (
            LearningResource.objects.create(
                title="Reported Resource",
                resource_key="reported-resource",
                provider="GradNavi Test",
                url="https://example.com/reported-resource",
                resource_type="tutorial",
                description="Resource under report review.",
                is_active=True,
                access_type="free",
                source_type="curated",
                health_status="active",
            )
        )

        self.report = (
            LearningResourceReport.objects.create(
                student_profile=self.student_profile,
                learning_resource=self.learning_resource,
                reason=(
                    LearningResourceReport
                    .Reason
                    .BROKEN_LINK
                ),
                comment="The resource link is broken.",
            )
        )

    def test_admin_can_list_learning_resource_reports(self):
        self.authenticate_admin()

        response = self.client.get(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data[0]["id"],
            self.report.id,
        )
        self.assertEqual(
            response.data[0]["student_profile"],
            self.student_profile.id,
        )
        self.assertNotIn(
            self.student.email,
            str(response.data),
        )

    def test_admin_can_retrieve_learning_resource_report(self):
        self.authenticate_admin()

        response = self.client.get(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
                f"{self.report.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            self.report.id,
        )
        self.assertEqual(
            response.data["reason"],
            LearningResourceReport.Reason.BROKEN_LINK,
        )

    def test_admin_can_change_report_status_to_resolved(self):
        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
                f"{self.report.id}/"
            ),
            {
                "status": (
                    LearningResourceReport
                    .Status
                    .RESOLVED
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.report.refresh_from_db()

        self.assertEqual(
            self.report.status,
            LearningResourceReport.Status.RESOLVED,
        )

    def test_admin_can_change_report_status_to_dismissed(self):
        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
                f"{self.report.id}/"
            ),
            {
                "status": (
                    LearningResourceReport
                    .Status
                    .DISMISSED
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.report.refresh_from_db()

        self.assertEqual(
            self.report.status,
            LearningResourceReport.Status.DISMISSED,
        )

    def test_invalid_report_status_is_rejected(self):
        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
                f"{self.report.id}/"
            ),
            {
                "status": "archived",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.report.refresh_from_db()

        self.assertEqual(
            self.report.status,
            LearningResourceReport.Status.OPEN,
        )

    def test_patch_cannot_alter_report_context_fields(self):
        other_user = User.objects.create_user(
            email="other-student@gradnavi.test",
            password=self.password,
        )
        other_profile = StudentProfile.objects.create(
            user=other_user,
        )
        other_resource = LearningResource.objects.create(
            title="Other Reported Resource",
            resource_key="other-reported-resource",
            provider="GradNavi Test",
            url="https://example.com/other-reported-resource",
            resource_type="tutorial",
            description="Other resource.",
            is_active=True,
            access_type="free",
            source_type="curated",
            health_status="active",
        )

        self.authenticate_admin()

        response = self.client.patch(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
                f"{self.report.id}/"
            ),
            {
                "student_profile": other_profile.id,
                "learning_resource": other_resource.id,
                "reason": LearningResourceReport.Reason.OUTDATED,
                "comment": "Changed by admin.",
                "status": (
                    LearningResourceReport
                    .Status
                    .RESOLVED
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.report.refresh_from_db()

        self.assertEqual(
            self.report.student_profile,
            self.student_profile,
        )
        self.assertEqual(
            self.report.learning_resource,
            self.learning_resource,
        )
        self.assertEqual(
            self.report.reason,
            LearningResourceReport.Reason.BROKEN_LINK,
        )
        self.assertEqual(
            self.report.comment,
            "The resource link is broken.",
        )
        self.assertEqual(
            self.report.status,
            LearningResourceReport.Status.RESOLVED,
        )

    def test_student_cannot_access_report_list(self):
        self.authenticate_student()

        response = self.client.get(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_student_cannot_access_report_detail_or_update(self):
        self.authenticate_student()

        detail_url = (
            "/api/v1/administration/"
            "learning-resource-reports/"
            f"{self.report.id}/"
        )

        retrieve_response = self.client.get(detail_url)

        self.assertEqual(
            retrieve_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        update_response = self.client.patch(
            detail_url,
            {
                "status": (
                    LearningResourceReport
                    .Status
                    .RESOLVED
                ),
            },
            format="json",
        )

        self.assertEqual(
            update_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_access_report_list(
        self,
    ):
        response = self.client.get(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_access_report_detail_or_update(
        self,
    ):
        detail_url = (
            "/api/v1/administration/"
            "learning-resource-reports/"
            f"{self.report.id}/"
        )

        retrieve_response = self.client.get(detail_url)

        self.assertEqual(
            retrieve_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        update_response = self.client.patch(
            detail_url,
            {
                "status": (
                    LearningResourceReport
                    .Status
                    .RESOLVED
                ),
            },
            format="json",
        )

        self.assertEqual(
            update_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class AdminAuditRecordTests(
    AdministrationAPITestCase
):
    def create_search_record(
        self,
        *,
        action,
        area,
        target_type,
        target_id,
        actor=None,
    ):
        return AuditRecord.objects.create(
            actor=actor or self.admin,
            action=action,
            area=area,
            target_type=target_type,
            target_id=str(target_id),
            metadata={},
        )

    def audit_search_results(self, term):
        self.authenticate_admin()

        response = self.client.get(
            (
                "/api/v1/administration/"
                f"audit-records/?search={term}"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        return response.data

    def test_admin_can_list_and_retrieve_audit_records(self):
        record = AuditRecord.objects.create(
            actor=self.admin,
            action="admin.test.action",
            area="users",
            target_type="User",
            target_id=str(self.student.id),
            metadata={
                "changed_fields": ["first_name"],
            },
        )

        self.authenticate_admin()

        list_response = self.client.get(
            "/api/v1/administration/audit-records/"
        )
        detail_response = self.client.get(
            (
                "/api/v1/administration/audit-records/"
                f"{record.id}/"
            )
        )

        self.assertEqual(
            list_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            detail_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            detail_response.data["id"],
            record.id,
        )
        self.assertEqual(
            detail_response.data["actor"],
            self.admin.id,
        )

    def test_audit_record_search_matches_action(self):
        matching = self.create_search_record(
            action="admin.career.search_action",
            area="careers",
            target_type="Career",
            target_id=1001,
        )
        self.create_search_record(
            action="admin.skill.other_action",
            area="skills",
            target_type="Skill",
            target_id=1002,
        )

        results = self.audit_search_results(
            "search_action"
        )

        self.assertEqual(
            [record["id"] for record in results],
            [matching.id],
        )

    def test_audit_record_search_matches_administrator(self):
        actor = User.objects.create_superuser(
            email="audit-search-admin@gradnavi.test",
            password=self.password,
            first_name="AuditSearchAdmin",
            last_name="Reviewer",
        )
        matching = self.create_search_record(
            action="admin.user.updated",
            area="users",
            target_type="User",
            target_id=self.student.id,
            actor=actor,
        )
        self.create_search_record(
            action="admin.user.status_changed",
            area="users",
            target_type="User",
            target_id=self.admin.id,
            actor=self.admin,
        )

        results = self.audit_search_results(
            "AuditSearchAdmin"
        )

        self.assertEqual(
            [record["id"] for record in results],
            [matching.id],
        )

    def test_audit_record_search_matches_target(self):
        matching = self.create_search_record(
            action="admin.learning_resource.updated",
            area="learning_resources",
            target_type="LearningResource",
            target_id="target-search-123",
        )
        self.create_search_record(
            action="admin.career.updated",
            area="careers",
            target_type="Career",
            target_id="other-target",
        )

        results = self.audit_search_results(
            "target-search-123"
        )

        self.assertEqual(
            [record["id"] for record in results],
            [matching.id],
        )

    def test_audit_record_search_matches_area(self):
        matching = self.create_search_record(
            action="admin.learning_resource_report.status_changed",
            area="learning_resource_reports",
            target_type="LearningResourceReport",
            target_id=1003,
        )
        self.create_search_record(
            action="admin.learning_resource.updated",
            area="learning_resources",
            target_type="LearningResource",
            target_id=1004,
        )

        results = self.audit_search_results(
            "learning_resource_reports"
        )

        self.assertEqual(
            [record["id"] for record in results],
            [matching.id],
        )

    def test_audit_record_search_returns_empty_for_nonmatch(self):
        self.create_search_record(
            action="admin.career.updated",
            area="careers",
            target_type="Career",
            target_id=1005,
        )

        results = self.audit_search_results(
            "not-present-in-audit-records"
        )

        self.assertEqual(results, [])

    def test_audit_records_endpoint_is_read_only(self):
        self.authenticate_admin()

        response = self.client.post(
            "/api/v1/administration/audit-records/",
            {
                "action": "admin.test.injected",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_audit_response_does_not_expose_user_email(self):
        AuditRecord.objects.create(
            actor=self.admin,
            action="admin.user.updated",
            area="users",
            target_type="User",
            target_id=str(self.student.id),
            metadata={
                "changed_fields": ["first_name"],
            },
        )

        self.authenticate_admin()

        response = self.client.get(
            "/api/v1/administration/audit-records/"
        )

        response_text = str(response.data)

        self.assertNotIn(
            self.admin.email,
            response_text,
        )
        self.assertNotIn(
            self.student.email,
            response_text,
        )
        self.assertNotIn(
            "password",
            response_text,
        )
        self.assertNotIn(
            "token",
            response_text,
        )

    def test_career_create_update_and_delete_create_audit_records(
        self,
    ):
        self.authenticate_admin()

        create_response = self.client.post(
            "/api/v1/administration/careers/",
            {
                "name": "Audited Career",
                "description": "Audited test career.",
                "category": "Testing",
                "active": True,
            },
            format="json",
        )
        career_id = create_response.data["id"]

        self.client.patch(
            (
                "/api/v1/administration/careers/"
                f"{career_id}/"
            ),
            {
                "category": "Audited",
            },
            format="json",
        )
        self.client.delete(
            (
                "/api/v1/administration/careers/"
                f"{career_id}/"
            )
        )

        self.assertTrue(
            AuditRecord.objects.filter(
                action="admin.career.created",
                area="careers",
                target_type="Career",
                target_id=str(career_id),
                actor=self.admin,
            ).exists()
        )
        self.assertTrue(
            AuditRecord.objects.filter(
                action="admin.career.updated",
                area="careers",
                target_type="Career",
                target_id=str(career_id),
                actor=self.admin,
                metadata={
                    "changed_fields": ["category"],
                },
            ).exists()
        )
        self.assertTrue(
            AuditRecord.objects.filter(
                action="admin.career.deleted",
                area="careers",
                target_type="Career",
                target_id=str(career_id),
                actor=self.admin,
            ).exists()
        )

    def test_learning_resource_report_status_change_creates_audit_record(
        self,
    ):
        profile = StudentProfile.objects.create(
            user=self.student,
        )
        resource = LearningResource.objects.create(
            title="Audited Report Resource",
            resource_key="audited-report-resource",
            provider="GradNavi Test",
            url="https://example.com/audited-report-resource",
            resource_type="tutorial",
            description="Reported resource.",
            is_active=True,
            access_type="free",
            source_type="curated",
            health_status="active",
        )
        report = LearningResourceReport.objects.create(
            student_profile=profile,
            learning_resource=resource,
            reason=LearningResourceReport.Reason.BROKEN_LINK,
            comment="Broken.",
        )

        self.authenticate_admin()

        self.client.patch(
            (
                "/api/v1/administration/"
                "learning-resource-reports/"
                f"{report.id}/"
            ),
            {
                "status": (
                    LearningResourceReport
                    .Status
                    .RESOLVED
                ),
            },
            format="json",
        )

        self.assertTrue(
            AuditRecord.objects.filter(
                action=(
                    "admin.learning_resource_report."
                    "status_changed"
                ),
                area="learning_resource_reports",
                target_type="LearningResourceReport",
                target_id=str(report.id),
                actor=self.admin,
                metadata={
                    "previous_status": (
                        LearningResourceReport.Status.OPEN
                    ),
                    "new_status": (
                        LearningResourceReport.Status.RESOLVED
                    ),
                },
            ).exists()
        )


class AdminAnalyticsTests(
    AdministrationAPITestCase
):
    analytics_url = (
        "/api/v1/administration/analytics/"
    )

    def create_student_profile(self, email):
        user = User.objects.create_user(
            email=email,
            password=self.password,
            first_name="Analytics",
            last_name="Student",
        )

        return StudentProfile.objects.create(
            user=user,
        )

    def create_career_goal(self, profile, career):
        return CareerGoal.objects.create(
            student_profile=profile,
            career=career,
            target_role=career.name,
        )

    def create_reference_dataset(self):
        source = ReferenceSource.objects.create(
            name="O*NET Database",
        )

        return ReferenceDataset.objects.create(
            source=source,
            version="31.0",
            retrieved_at=date(2026, 1, 1),
            status=ReferenceDataset.Status.ACTIVE,
        )

    def create_requirement(
        self,
        *,
        career,
        skill,
        dataset,
        required_level=Decimal("75.00"),
        importance=Decimal("80.00"),
    ):
        career_skill = CareerSkill.objects.create(
            career=career,
            skill=skill,
            importance_score=importance,
            required_level_score=required_level,
            review_status=ReviewStatus.APPROVED,
        )

        return CareerSkillEvidence.objects.create(
            career_skill=career_skill,
            dataset=dataset,
            external_occupation_id=(
                f"career-{career.id}"
            ),
            external_skill_id=(
                f"skill-{skill.id}"
            ),
            source_domain="onet_essential_skills",
            source_relation="essential",
            normalized_importance=importance,
            normalized_level=required_level,
        )

    def create_skill_gap_fixture(self):
        dataset = self.create_reference_dataset()

        career = Career.objects.create(
            name="Analytics Software Engineer",
            description="Analytics test career.",
            category="Technology",
            active=True,
        )

        missing_skill = Skill.objects.create(
            name="Analytics Missing Skill",
            concept_type=Skill.ConceptType.SKILL,
        )
        below_skill = Skill.objects.create(
            name="Analytics Below Skill",
            concept_type=Skill.ConceptType.SKILL,
        )
        meets_skill = Skill.objects.create(
            name="Analytics Meets Skill",
            concept_type=Skill.ConceptType.SKILL,
        )

        self.create_requirement(
            career=career,
            skill=missing_skill,
            dataset=dataset,
        )
        self.create_requirement(
            career=career,
            skill=below_skill,
            dataset=dataset,
        )
        self.create_requirement(
            career=career,
            skill=meets_skill,
            dataset=dataset,
        )

        first_profile = self.create_student_profile(
            "analytics-gap-a@gradnavi.test"
        )
        second_profile = self.create_student_profile(
            "analytics-gap-b@gradnavi.test"
        )

        self.create_career_goal(
            first_profile,
            career,
        )
        self.create_career_goal(
            second_profile,
            career,
        )

        for profile in (
            first_profile,
            second_profile,
        ):
            StudentSkill.objects.create(
                student_profile=profile,
                skill=below_skill,
                proficiency_level=(
                    StudentSkill
                    .ProficiencyLevel
                    .DEVELOPING
                ),
            )
            StudentSkill.objects.create(
                student_profile=profile,
                skill=meets_skill,
                proficiency_level=(
                    StudentSkill
                    .ProficiencyLevel
                    .ADVANCED
                ),
            )

        return (
            missing_skill,
            below_skill,
            meets_skill,
        )

    def get_analytics(self):
        self.authenticate_admin()

        return self.client.get(
            self.analytics_url
        )

    def test_admin_can_get_analytics_endpoint(self):
        response = self.get_analytics()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            set(response.data),
            {
                "popular_careers",
                "common_skill_gaps",
            },
        )

    def test_unauthenticated_request_receives_401(self):
        response = self.client.get(
            self.analytics_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_student_request_receives_403(self):
        self.authenticate_student()

        response = self.client.get(
            self.analytics_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_analytics_endpoint_is_read_only(self):
        self.authenticate_admin()

        for method in (
            self.client.post,
            self.client.put,
            self.client.patch,
            self.client.delete,
        ):
            with self.subTest(method=method.__name__):
                response = method(
                    self.analytics_url,
                    {},
                    format="json",
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                )

    def test_empty_state_returns_empty_aggregate_lists(self):
        response = self.get_analytics()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            {
                "popular_careers": [],
                "common_skill_gaps": [],
            },
        )

    def test_popular_careers_aggregate_career_goal_counts(
        self,
    ):
        career = Career.objects.create(
            name="Analytics Data Analyst",
            active=True,
        )
        first_profile = self.create_student_profile(
            "analytics-popular-a@gradnavi.test"
        )
        second_profile = self.create_student_profile(
            "analytics-popular-b@gradnavi.test"
        )

        self.create_career_goal(
            first_profile,
            career,
        )
        self.create_career_goal(
            second_profile,
            career,
        )

        response = self.get_analytics()

        self.assertEqual(
            response.data["popular_careers"],
            [
                {
                    "career_id": career.id,
                    "career_name": career.name,
                    "selection_count": 2,
                }
            ],
        )

    def test_different_careers_produce_separate_aggregates(
        self,
    ):
        first_career = Career.objects.create(
            name="Analytics Career A",
            active=True,
        )
        second_career = Career.objects.create(
            name="Analytics Career B",
            active=True,
        )
        first_profile = self.create_student_profile(
            "analytics-career-a@gradnavi.test"
        )
        second_profile = self.create_student_profile(
            "analytics-career-b@gradnavi.test"
        )

        self.create_career_goal(
            first_profile,
            first_career,
        )
        self.create_career_goal(
            second_profile,
            second_career,
        )

        response = self.get_analytics()

        self.assertEqual(
            response.data["popular_careers"],
            [
                {
                    "career_id": first_career.id,
                    "career_name": first_career.name,
                    "selection_count": 1,
                },
                {
                    "career_id": second_career.id,
                    "career_name": second_career.name,
                    "selection_count": 1,
                },
            ],
        )

    def test_popular_career_ordering_is_deterministic(
        self,
    ):
        alpha = Career.objects.create(
            name="Analytics Alpha Career",
            active=True,
        )
        beta = Career.objects.create(
            name="Analytics Beta Career",
            active=True,
        )
        gamma = Career.objects.create(
            name="Analytics Gamma Career",
            active=True,
        )

        for index, career in enumerate(
            (gamma, gamma, alpha, beta),
        ):
            profile = self.create_student_profile(
                (
                    "analytics-order-"
                    f"{index}@gradnavi.test"
                )
            )
            self.create_career_goal(
                profile,
                career,
            )

        response = self.get_analytics()

        self.assertEqual(
            [
                item["career_name"]
                for item
                in response.data["popular_careers"]
            ],
            [
                gamma.name,
                alpha.name,
                beta.name,
            ],
        )

    def test_common_skill_gaps_count_missing_and_below(
        self,
    ):
        (
            missing_skill,
            below_skill,
            meets_skill,
        ) = self.create_skill_gap_fixture()

        response = self.get_analytics()

        gaps = {
            row["skill_id"]: row
            for row
            in response.data["common_skill_gaps"]
        }

        self.assertEqual(
            gaps[missing_skill.id][
                "affected_student_count"
            ],
            2,
        )
        self.assertEqual(
            gaps[below_skill.id][
                "affected_student_count"
            ],
            2,
        )
        self.assertNotIn(
            meets_skill.id,
            gaps,
        )

    def test_common_skill_gap_ordering_is_deterministic(
        self,
    ):
        self.create_skill_gap_fixture()

        response = self.get_analytics()

        self.assertEqual(
            [
                item["skill_name"]
                for item
                in response.data["common_skill_gaps"]
            ],
            [
                "Analytics Below Skill",
                "Analytics Missing Skill",
            ],
        )

    def test_analytics_response_exposes_no_student_data(
        self,
    ):
        self.create_skill_gap_fixture()

        response = self.get_analytics()

        response_text = str(response.data)

        self.assertNotIn(
            "student_profile",
            response_text,
        )
        self.assertNotIn(
            "user",
            response_text,
        )
        self.assertNotIn(
            "email",
            response_text,
        )
        self.assertNotIn(
            "analytics-gap-a@gradnavi.test",
            response_text,
        )
        self.assertNotIn(
            "analytics-gap-b@gradnavi.test",
            response_text,
        )


class AdministrationURLRoutingTests(APITestCase):
    def test_administration_routes_are_registered(self):
        expected_routes = {
            "/api/v1/administration/analytics/":
                "admin-analytics",
            "/api/v1/administration/audit-records/":
                "admin-audit-record-list",
            "/api/v1/administration/users/":
                "admin-user-list",
            "/api/v1/administration/users/1/role/":
                "admin-user-role",
            "/api/v1/administration/users/1/status/":
                "admin-user-status",
            "/api/v1/administration/careers/":
                "admin-career-list",
            "/api/v1/administration/skills/":
                "admin-skill-list",
            "/api/v1/administration/learning-resources/":
                "admin-learning-resource-list",
            "/api/v1/administration/learning-resource-reports/":
                "admin-learning-resource-report-list",
        }

        for path, expected_name in expected_routes.items():
            with self.subTest(path=path):
                self.assertEqual(
                    resolve(path).url_name,
                    expected_name,
                )
