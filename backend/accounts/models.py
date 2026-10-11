import os
import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email address must be set.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields["role"] = User.Role.STUDENT
        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("role") != User.Role.ADMIN:
            raise ValueError("Superuser must have role=admin.")

        return self._create_user(email, password, **extra_fields)


def profile_photo_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1].lower()

    return (
        f"profile_photos/user_{instance.pk}/"
        f"{uuid.uuid4().hex}{extension}"
    )


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        ADMIN = "admin", "Administrator"

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    profile_photo = models.ImageField(
        upload_to=profile_photo_upload_to,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def delete_profile_photo(self, *, save=True):
        if not self.profile_photo:
            return

        storage = self.profile_photo.storage
        name = self.profile_photo.name

        self.profile_photo = None

        if save:
            self.save(
                update_fields=["profile_photo"]
            )

        if (
            name
            and storage.exists(name)
        ):
            storage.delete(name)

    def __str__(self):
        return self.email
