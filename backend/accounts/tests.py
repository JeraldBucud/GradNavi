from django.contrib.auth import get_user_model
from django.urls import Resolver404, resolve
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


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
