from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import override_settings
from django.urls import Resolver404, resolve
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from profiles.models import CareerGoal, StudentProfile


User = get_user_model()


def assert_error_envelope(test_case, response, code, details_key=None):
    test_case.assertIn("error", response.data)
    test_case.assertEqual(response.data["error"]["code"], code)
    test_case.assertIn("message", response.data["error"])
    if details_key is not None:
        test_case.assertIn("details", response.data["error"])
        test_case.assertIn(details_key, response.data["error"]["details"])


class RegistrationAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/register/"
        self.valid_payload = {
            "email": "student@example.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
            "first_name": "John",
            "last_name": "Smith",
        }

    def test_successful_registration_returns_201_and_safe_user_fields(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data.keys()),
            {"id", "email", "first_name", "last_name", "role"},
        )
        self.assertEqual(response.data["email"], "student@example.com")
        self.assertEqual(response.data["first_name"], "John")
        self.assertEqual(response.data["last_name"], "Smith")
        self.assertEqual(response.data["role"], User.Role.STUDENT)
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_confirm", response.data)

    def test_successful_registration_stores_user_in_database(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="student@example.com").exists())

    def test_successful_registration_creates_exactly_one_empty_student_profile(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="student@example.com")
        profile = StudentProfile.objects.get(user=user)
        self.assertEqual(StudentProfile.objects.filter(user=user).count(), 1)
        self.assertFalse(profile.student_skills.exists())
        self.assertFalse(profile.student_interests.exists())
        self.assertFalse(profile.education.exists())
        self.assertFalse(profile.experience.exists())
        self.assertFalse(profile.projects.exists())
        self.assertFalse(profile.career_goals.exists())
        self.assertFalse(profile.personality_responses.exists())

    def test_password_is_hashed_and_checkable(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="student@example.com")
        self.assertNotEqual(user.password, self.valid_payload["password"])
        self.assertTrue(user.check_password(self.valid_payload["password"]))

    def test_default_role_is_student(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="student@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        User.objects.create_user(
            email="student@example.com",
            password="StrongPassword123!",
            first_name="Existing",
            last_name="Student",
        )
        payload = {
            **self.valid_payload,
            "email": "STUDENT@example.com",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        assert_error_envelope(self, response, "conflict", "email")

    def test_password_mismatch_is_rejected(self):
        payload = {
            **self.valid_payload,
            "password_confirm": "DifferentPassword123!",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error", "password_confirm")
        self.assertFalse(User.objects.exists())
        self.assertFalse(StudentProfile.objects.exists())

    def test_weak_password_is_rejected(self):
        payload = {
            **self.valid_payload,
            "password": "password",
            "password_confirm": "password",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error", "password")
        self.assertFalse(User.objects.exists())

    def test_required_fields_are_rejected_when_missing(self):
        required_fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
        )

        for field in required_fields:
            with self.subTest(field=field):
                payload = self.valid_payload.copy()
                payload.pop(field)

                response = self.client.post(self.url, payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                assert_error_envelope(self, response, "validation_error", field)

    def test_public_registration_cannot_create_privileged_user(self):
        payload = {
            **self.valid_payload,
            "email": "hacker@example.com",
            "role": User.Role.ADMIN,
            "is_staff": True,
            "is_superuser": True,
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="hacker@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_registration_response_remains_compatible_after_profile_creation(self):
        response = self.client.post(self.url, self.valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data.keys()),
            {"id", "email", "first_name", "last_name", "role"},
        )
        self.assertNotIn("student_profile", response.data)
        self.assertNotIn("profile", response.data)

    def test_newly_registered_student_can_get_empty_profile_then_patch_and_refetch(self):
        register_response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": self.valid_payload["email"],
                "password": self.valid_payload["password"],
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data["access"]

        profile_response = self.client.get(
            "/api/v1/profile/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            profile_response.data["data"]["profile"],
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

        patch_response = self.client.patch(
            "/api/v1/profile/",
            {"career_goals": ["Software Engineer"]},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        refetch_response = self.client.get(
            "/api/v1/profile/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(refetch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            refetch_response.data["data"]["profile"]["career_goals"],
            [
                {
                    "id": CareerGoal.objects.get(
                        student_profile__user__email="student@example.com"
                    ).id,
                    "target_role": "Software Engineer",
                    "description": "",
                }
            ],
        )


class LoginAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/login/"
        self.password = "GradNaviTest123!"
        self.user = User.objects.create_user(
            email="student1@gradnavi.test",
            password=self.password,
            first_name="Test",
            last_name="Student",
        )

    def test_successful_login_returns_tokens_and_safe_user_information(self):
        response = self.client.post(
            self.url,
            {
                "email": "student1@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {"access", "refresh", "user"})
        self.assertEqual(
            set(response.data["user"].keys()),
            {"id", "email", "first_name", "last_name", "role"},
        )
        self.assertEqual(response.data["user"]["id"], self.user.id)
        self.assertEqual(response.data["user"]["email"], "student1@gradnavi.test")
        self.assertEqual(response.data["user"]["first_name"], "Test")
        self.assertEqual(response.data["user"]["last_name"], "Student")
        self.assertEqual(response.data["user"]["role"], User.Role.STUDENT)

    def test_successful_login_accepts_email_case_insensitively(self):
        response = self.client.post(
            self.url,
            {
                "email": "STUDENT1@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "student1@gradnavi.test")

    def test_successful_login_issues_valid_jwt_tokens(self):
        response = self.client.post(
            self.url,
            {
                "email": "student1@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        try:
            access = AccessToken(response.data["access"])
            refresh = RefreshToken(response.data["refresh"])
        except TokenError as exc:
            self.fail(f"Login returned invalid JWT tokens: {exc}")

        self.assertEqual(access["user_id"], str(self.user.id))
        self.assertEqual(refresh["user_id"], str(self.user.id))

    def test_wrong_password_is_rejected_with_safe_error(self):
        response = self.client.post(
            self.url,
            {
                "email": "student1@gradnavi.test",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "invalid_credentials")
        self.assertNotIn("email", response.data["error"].get("details", {}))

    def test_nonexistent_email_is_rejected_with_same_safe_error(self):
        response = self.client.post(
            self.url,
            {
                "email": "missing@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "invalid_credentials")
        self.assertNotIn("email", response.data["error"].get("details", {}))

    def test_wrong_password_and_nonexistent_email_return_same_error(self):
        wrong_password_response = self.client.post(
            self.url,
            {
                "email": "student1@gradnavi.test",
                "password": "WrongPassword123!",
            },
            format="json",
        )
        nonexistent_email_response = self.client.post(
            self.url,
            {
                "email": "missing@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            wrong_password_response.status_code,
            nonexistent_email_response.status_code,
        )
        self.assertEqual(
            wrong_password_response.data["error"],
            nonexistent_email_response.data["error"],
        )

    def test_missing_credentials_are_rejected(self):
        for payload, missing_field in (
            ({"password": self.password}, "email"),
            ({"email": "student1@gradnavi.test"}, "password"),
        ):
            with self.subTest(missing_field=missing_field):
                response = self.client.post(self.url, payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                assert_error_envelope(
                    self,
                    response,
                    "validation_error",
                    missing_field,
                )

    def test_inactive_user_is_rejected(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            self.url,
            {
                "email": "student1@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "invalid_credentials")

    def test_login_response_does_not_leak_password_or_privileged_fields(self):
        response = self.client.post(
            self.url,
            {
                "email": "student1@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_text = str(response.data)
        self.assertNotIn("password", response.data["user"])
        self.assertNotIn("password", response_text)
        self.assertNotIn(self.user.password, response_text)
        self.assertNotIn("is_staff", response.data["user"])
        self.assertNotIn("is_superuser", response.data["user"])

    def test_login_does_not_modify_user_role(self):
        self.assertEqual(self.user.role, User.Role.STUDENT)

        response = self.client.post(
            self.url,
            {
                "email": "student1@gradnavi.test",
                "password": self.password,
                "role": User.Role.ADMIN,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.Role.STUDENT)


class AuthenticationURLRoutingTests(APITestCase):
    def test_v1_registration_and_login_routes_are_registered(self):
        self.assertEqual(resolve("/api/v1/auth/register/").url_name, "register")
        self.assertEqual(resolve("/api/v1/auth/login/").url_name, "login")

    def test_legacy_auth_routes_are_not_registered(self):
        for path in ("/api/auth/register/", "/api/auth/login/"):
            with self.subTest(path=path):
                with self.assertRaises(Resolver404):
                    resolve(path)


class TokenRefreshAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/token/refresh/"
        self.password = "GradNaviTest123!"
        self.user = User.objects.create_user(
            email="refresh@gradnavi.test",
            password=self.password,
            first_name="Refresh",
            last_name="Student",
        )
        self.login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "refresh@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )
        self.refresh_token = self.login_response.data["refresh"]
        self.access_token = self.login_response.data["access"]

    def test_valid_refresh_token_succeeds_and_returns_rotated_tokens(self):
        response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.keys()), {"access", "refresh"})
        self.assertNotEqual(response.data["refresh"], self.refresh_token)

        try:
            access = AccessToken(response.data["access"])
            refresh = RefreshToken(response.data["refresh"])
        except TokenError as exc:
            self.fail(f"Refresh returned invalid JWT tokens: {exc}")

        self.assertEqual(access["user_id"], str(self.user.id))
        self.assertEqual(refresh["user_id"], str(self.user.id))

    def test_original_refresh_token_cannot_be_reused_after_rotation(self):
        first_response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json",
        )
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(second_response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, second_response, "token_not_valid")

    def test_new_rotated_refresh_token_can_be_used_for_another_refresh(self):
        first_response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json",
        )
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.client.post(
            self.url,
            {"refresh": first_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", second_response.data)
        self.assertIn("refresh", second_response.data)
        self.assertNotEqual(second_response.data["refresh"], first_response.data["refresh"])

    def test_malformed_refresh_token_is_rejected(self):
        response = self.client.post(
            self.url,
            {"refresh": "not-a-valid-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "token_not_valid")

    def test_access_token_cannot_be_used_as_refresh_token(self):
        response = self.client.post(
            self.url,
            {"refresh": self.access_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "token_not_valid")

    def test_missing_refresh_field_is_rejected(self):
        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error", "refresh")

    def test_refresh_route_is_registered(self):
        self.assertEqual(
            resolve("/api/v1/auth/token/refresh/").url_name,
            "token-refresh",
        )


class CurrentUserAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/me/"
        self.password = "GradNaviTest123!"
        self.user = User.objects.create_user(
            email="student1@gradnavi.test",
            password=self.password,
            first_name="Test",
            last_name="Student",
        )
        self.other_user = User.objects.create_user(
            email="other@gradnavi.test",
            password=self.password,
            first_name="Other",
            last_name="Student",
        )
        self.login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "student1@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )
        self.access_token = self.login_response.data["access"]
        self.refresh_token = self.login_response.data["refresh"]

    def test_valid_access_token_returns_current_user(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": self.user.id,
                "email": "student1@gradnavi.test",
                "first_name": "Test",
                "last_name": "Student",
                "role": User.Role.STUDENT,
            },
        )

    def test_current_user_response_contains_safe_fields_only(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {"id", "email", "first_name", "last_name", "role"},
        )
        response_text = str(response.data)
        self.assertNotIn("password", response.data)
        self.assertNotIn("password", response_text)
        self.assertNotIn(self.user.password, response_text)
        self.assertNotIn("refresh", response.data)
        self.assertNotIn("is_staff", response.data)
        self.assertNotIn("is_superuser", response.data)
        self.assertNotIn("groups", response.data)
        self.assertNotIn("permissions", response.data)

    def test_missing_authorization_header_is_rejected(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "not_authenticated")

    def test_malformed_token_is_rejected(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION="Bearer not-a-valid-token",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "token_not_valid")

    def test_refresh_token_cannot_authenticate_current_user_endpoint(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.refresh_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "token_not_valid")

    def test_another_users_access_token_returns_that_user(self):
        other_login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "other@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {other_login_response.data['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.other_user.id)
        self.assertEqual(response.data["email"], "other@gradnavi.test")
        self.assertEqual(response.data["first_name"], "Other")
        self.assertNotEqual(response.data["id"], self.user.id)

    def test_current_user_route_is_registered(self):
        self.assertEqual(resolve("/api/v1/auth/me/").url_name, "me")

    def test_legacy_current_user_route_is_not_registered(self):
        with self.assertRaises(Resolver404):
            resolve("/api/auth/me/")


class LogoutAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/v1/auth/logout/"
        self.password = "GradNaviTest123!"
        self.user = User.objects.create_user(
            email="logout@gradnavi.test",
            password=self.password,
            first_name="Logout",
            last_name="Student",
        )
        self.login_response = self.client.post(
            "/api/v1/auth/login/",
            {
                "email": "logout@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )
        self.access_token = self.login_response.data["access"]
        self.refresh_token = self.login_response.data["refresh"]

    def authenticated_post(self, payload):
        return self.client.post(
            self.url,
            payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

    def test_successful_logout_blacklists_submitted_refresh_token(self):
        response = self.authenticated_post({"refresh": self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Logged out successfully."})

        refresh_response = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": self.refresh_token},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, refresh_response, "token_not_valid")

    def test_missing_bearer_authentication_is_rejected(self):
        response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "not_authenticated")

    def test_invalid_bearer_authentication_is_rejected(self):
        response = self.client.post(
            self.url,
            {"refresh": self.refresh_token},
            format="json",
            HTTP_AUTHORIZATION="Bearer not-a-valid-token",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "token_not_valid")

    def test_missing_refresh_token_is_rejected(self):
        response = self.authenticated_post({})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error", "refresh")

    def test_malformed_refresh_token_is_rejected(self):
        response = self.authenticated_post({"refresh": "not-a-valid-token"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "token_not_valid")

    def test_access_token_cannot_be_used_as_refresh_token(self):
        response = self.authenticated_post({"refresh": self.access_token})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "token_not_valid")

    def test_already_blacklisted_refresh_token_is_safely_rejected(self):
        first_response = self.authenticated_post({"refresh": self.refresh_token})
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        second_response = self.authenticated_post({"refresh": self.refresh_token})

        self.assertEqual(second_response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, second_response, "token_not_valid")

    def test_existing_access_token_remains_usable_until_expiry_after_logout(self):
        logout_response = self.authenticated_post({"refresh": self.refresh_token})
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        current_user_response = self.client.get(
            "/api/v1/auth/me/",
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(current_user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_user_response.data["id"], self.user.id)

    def test_logout_route_is_registered(self):
        self.assertEqual(resolve("/api/v1/auth/logout/").url_name, "logout")

    def test_legacy_logout_route_is_not_registered(self):
        with self.assertRaises(Resolver404):
            resolve("/api/auth/logout/")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    MAILERS={"default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"}},
)
class PasswordResetAPITests(APITestCase):
    def setUp(self):
        self.reset_url = "/api/v1/auth/password/reset/"
        self.confirm_url = "/api/v1/auth/password/reset/confirm/"
        self.old_password = "GradNaviOld123!"
        self.new_password = "GradNaviNew123!"
        self.user = User.objects.create_user(
            email="reset@gradnavi.test",
            password=self.old_password,
            first_name="Reset",
            last_name="Student",
        )

    def make_reset_credentials(self, user=None):
        user = user or self.user
        return {
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        }

    def assert_standard_message_response(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"message": "If the email is registered, a password reset email has been sent."},
        )

    def test_existing_email_request_succeeds_and_sends_one_email(self):
        response = self.client.post(
            self.reset_url,
            {"email": "reset@gradnavi.test"},
            format="json",
        )

        self.assert_standard_message_response(response)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["reset@gradnavi.test"])

    def test_unknown_email_request_returns_same_safe_response_and_sends_no_email(self):
        existing_response = self.client.post(
            self.reset_url,
            {"email": "reset@gradnavi.test"},
            format="json",
        )
        mail.outbox.clear()

        unknown_response = self.client.post(
            self.reset_url,
            {"email": "missing@gradnavi.test"},
            format="json",
        )

        self.assertEqual(existing_response.status_code, unknown_response.status_code)
        self.assertEqual(existing_response.data, unknown_response.data)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_request_response_does_not_expose_uid_or_token(self):
        response = self.client.post(
            self.reset_url,
            {"email": "reset@gradnavi.test"},
            format="json",
        )

        response_text = str(response.data).lower()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("uid", response_text)
        self.assertNotIn("token", response_text)

    def test_missing_or_malformed_email_is_rejected(self):
        for payload in ({}, {"email": "not-an-email"}):
            with self.subTest(payload=payload):
                response = self.client.post(self.reset_url, payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                assert_error_envelope(self, response, "validation_error", "email")

    def test_valid_reset_confirm_changes_password(self):
        credentials = self.make_reset_credentials()
        response = self.client.post(
            self.confirm_url,
            {
                **credentials,
                "password": self.new_password,
                "password_confirm": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Password has been reset successfully."})

        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.old_password))
        self.assertTrue(self.user.check_password(self.new_password))

    def test_old_password_login_fails_and_new_password_login_succeeds_after_reset(self):
        credentials = self.make_reset_credentials()
        reset_response = self.client.post(
            self.confirm_url,
            {
                **credentials,
                "password": self.new_password,
                "password_confirm": self.new_password,
            },
            format="json",
        )
        self.assertEqual(reset_response.status_code, status.HTTP_200_OK)

        old_login_response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "reset@gradnavi.test", "password": self.old_password},
            format="json",
        )
        new_login_response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "reset@gradnavi.test", "password": self.new_password},
            format="json",
        )

        self.assertEqual(old_login_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(new_login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", new_login_response.data)
        self.assertIn("refresh", new_login_response.data)

    def test_used_reset_token_cannot_be_reused(self):
        credentials = self.make_reset_credentials()
        payload = {
            **credentials,
            "password": self.new_password,
            "password_confirm": self.new_password,
        }

        first_response = self.client.post(self.confirm_url, payload, format="json")
        second_response = self.client.post(self.confirm_url, payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, second_response, "invalid_reset_token")

    def test_invalid_token_is_rejected(self):
        credentials = self.make_reset_credentials()
        response = self.client.post(
            self.confirm_url,
            {
                **credentials,
                "token": "invalid-token",
                "password": self.new_password,
                "password_confirm": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "invalid_reset_token")

    def test_malformed_uid_is_rejected(self):
        credentials = self.make_reset_credentials()
        response = self.client.post(
            self.confirm_url,
            {
                **credentials,
                "uid": "not-a-valid-uid",
                "password": self.new_password,
                "password_confirm": self.new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        assert_error_envelope(self, response, "invalid_reset_token")

    def test_weak_password_is_rejected(self):
        credentials = self.make_reset_credentials()
        response = self.client.post(
            self.confirm_url,
            {
                **credentials,
                "password": "password",
                "password_confirm": "password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error", "password")

    def test_password_mismatch_is_rejected(self):
        credentials = self.make_reset_credentials()
        response = self.client.post(
            self.confirm_url,
            {
                **credentials,
                "password": self.new_password,
                "password_confirm": "DifferentPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        assert_error_envelope(self, response, "validation_error", "password_confirm")

    def test_reset_confirm_missing_required_fields_are_rejected(self):
        required_fields = ("uid", "token", "password", "password_confirm")
        credentials = self.make_reset_credentials()
        payload = {
            **credentials,
            "password": self.new_password,
            "password_confirm": self.new_password,
        }

        for field in required_fields:
            with self.subTest(field=field):
                invalid_payload = payload.copy()
                invalid_payload.pop(field)
                response = self.client.post(self.confirm_url, invalid_payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                assert_error_envelope(self, response, "validation_error", field)

    def test_password_reset_routes_are_registered(self):
        self.assertEqual(
            resolve("/api/v1/auth/password/reset/").url_name,
            "password-reset",
        )
        self.assertEqual(
            resolve("/api/v1/auth/password/reset/confirm/").url_name,
            "password-reset-confirm",
        )

    def test_legacy_password_reset_routes_are_not_registered(self):
        for path in (
            "/api/auth/password/reset/",
            "/api/auth/password/reset/confirm/",
        ):
            with self.subTest(path=path):
                with self.assertRaises(Resolver404):
                    resolve(path)
