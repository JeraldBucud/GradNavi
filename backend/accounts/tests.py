from django.contrib.auth import get_user_model
from django.urls import Resolver404, resolve
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


User = get_user_model()


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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_password_mismatch_is_rejected(self):
        payload = {
            **self.valid_payload,
            "password_confirm": "DifferentPassword123!",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)
        self.assertFalse(User.objects.exists())

    def test_weak_password_is_rejected(self):
        payload = {
            **self.valid_payload,
            "password": "password",
            "password_confirm": "password",
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)
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
                self.assertIn(field, response.data)

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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertNotIn("email", response.data)

    def test_nonexistent_email_is_rejected_with_same_safe_error(self):
        response = self.client.post(
            self.url,
            {
                "email": "missing@gradnavi.test",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertNotIn("email", response.data)

    def test_missing_credentials_are_rejected(self):
        for payload, missing_field in (
            ({"password": self.password}, "email"),
            ({"email": "student1@gradnavi.test"}, "password"),
        ):
            with self.subTest(missing_field=missing_field):
                response = self.client.post(self.url, payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(missing_field, response.data)

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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

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
