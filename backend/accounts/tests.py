from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class RegistrationAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("accounts:register")
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
