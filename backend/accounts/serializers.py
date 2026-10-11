import os

from PIL import Image, UnidentifiedImageError
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from gradnavi.exceptions import ConflictError
from profiles.models import StudentProfile


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "role",
        )
        read_only_fields = ("id", "role")
        extra_kwargs = {
            "email": {"required": True, "validators": []},
            "first_name": {"required": True, "allow_blank": False},
            "last_name": {"required": True, "allow_blank": False},
        }

    def validate_email(self, value):
        email = User.objects.normalize_email(value).lower()

        if User.objects.filter(email__iexact=email).exists():
            raise ConflictError(
                {
                    "message": "A user with this email already exists.",
                    "details": {
                        "email": ["A user with this email already exists."],
                    },
                }
            )

        return email

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Password confirmation does not match."}
            )

        try:
            validate_password(password)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        with transaction.atomic():
            user = User.objects.create_user(password=password, **validated_data)
            StudentProfile.objects.get_or_create(user=user)
            return user


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role")
        read_only_fields = fields




PROFILE_PHOTO_MAX_BYTES = 5 * 1024 * 1024

PROFILE_PHOTO_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

PROFILE_PHOTO_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}

PROFILE_PHOTO_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


class AccountSettingsSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "profile_photo",
        )
        read_only_fields = (
            "id",
            "email",
            "role",
        )

    def validate_first_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "First name cannot be blank."
            )

        return value

    def validate_last_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Last name cannot be blank."
            )

        return value

    def validate_profile_photo(self, value):
        if value is None:
            return value

        if value.size > PROFILE_PHOTO_MAX_BYTES:
            raise serializers.ValidationError(
                "Profile photo must be 5 MB or smaller."
            )

        content_type = (
            getattr(
                value,
                "content_type",
                "",
            )
            or ""
        ).lower()

        if content_type not in PROFILE_PHOTO_CONTENT_TYPES:
            raise serializers.ValidationError(
                "Profile photo must be a JPEG, PNG, or WebP image."
            )

        extension = os.path.splitext(
            value.name
        )[1].lower()

        if extension not in PROFILE_PHOTO_EXTENSIONS:
            raise serializers.ValidationError(
                "Profile photo must use a .jpg, .jpeg, .png, or .webp extension."
            )

        try:
            value.seek(0)

            with Image.open(value) as image:
                image_format = image.format
                image.verify()

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ) as exc:
            raise serializers.ValidationError(
                "Profile photo is not a valid image."
            ) from exc

        finally:
            value.seek(0)

        if image_format not in PROFILE_PHOTO_FORMATS:
            raise serializers.ValidationError(
                "Profile photo must be a JPEG, PNG, or WebP image."
            )

        return value

    def update(self, instance, validated_data):
        old_photo_name = (
            instance.profile_photo.name
            if instance.profile_photo
            else ""
        )

        old_photo_storage = (
            instance.profile_photo.storage
            if instance.profile_photo
            else None
        )

        photo_was_submitted = (
            "profile_photo"
            in validated_data
        )

        instance = super().update(
            instance,
            validated_data,
        )

        new_photo_name = (
            instance.profile_photo.name
            if instance.profile_photo
            else ""
        )

        if (
            photo_was_submitted
            and old_photo_name
            and old_photo_name
            != new_photo_name
            and old_photo_storage
            and old_photo_storage.exists(
                old_photo_name
            )
        ):
            old_photo_storage.delete(
                old_photo_name
            )

        return instance


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        current_password = attrs[
            "current_password"
        ]
        new_password = attrs[
            "new_password"
        ]
        new_password_confirm = attrs[
            "new_password_confirm"
        ]

        if not user.check_password(
            current_password
        ):
            raise serializers.ValidationError(
                {
                    "current_password":
                        "Current password is incorrect."
                }
            )

        if (
            new_password
            != new_password_confirm
        ):
            raise serializers.ValidationError(
                {
                    "new_password_confirm":
                        "Password confirmation does not match."
                }
            )

        if user.check_password(
            new_password
        ):
            raise serializers.ValidationError(
                {
                    "new_password":
                        "New password must be different from the current password."
                }
            )

        try:
            validate_password(
                new_password,
                user=user,
            )

        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {
                    "new_password":
                        list(exc.messages)
                }
            )

        attrs["user"] = user

        return attrs

    def save(self):
        user = self.validated_data["user"]

        user.set_password(
            self.validated_data[
                "new_password"
            ]
        )

        user.save(
            update_fields=["password"]
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    default_error_messages = {
        "invalid_credentials": "Unable to log in with the provided credentials.",
    }

    def validate(self, attrs):
        email = User.objects.normalize_email(attrs["email"]).lower()
        password = attrs["password"]
        request = self.context.get("request")

        user = authenticate(request=request, email=email, password=password)

        if user is None:
            raise AuthenticationFailed(
                self.error_messages["invalid_credentials"],
                code="invalid_credentials",
            )

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user,
        }

    def to_representation(self, instance):
        return {
            "access": instance["access"],
            "refresh": instance["refresh"],
            "user": UserSummarySerializer(instance["user"]).data,
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    default_error_messages = {
        "invalid_token": "Refresh token is invalid or expired.",
    }

    def validate(self, attrs):
        try:
            token = RefreshToken(attrs["refresh"])
            token.blacklist()
        except TokenError:
            raise AuthenticationFailed(
                self.error_messages["invalid_token"],
                code="token_not_valid",
            )

        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return User.objects.normalize_email(value).lower()

    def save(self):
        user = (
            User.objects.filter(email__iexact=self.validated_data["email"], is_active=True)
            .order_by("pk")
            .first()
        )

        if user is None:
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_path = f"/password/reset/confirm/?uid={uid}&token={token}"

        send_mail(
            subject="Reset your GradNavi password",
            message=(
                "Use the following GradNavi password reset details to set a new password.\n\n"
                f"UID: {uid}\n"
                f"Token: {token}\n\n"
                f"Development reset path: {reset_path}\n\n"
                "If you did not request this password reset, you can ignore this email."
            ),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[user.email],
            fail_silently=False,
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True, write_only=True)
    token = serializers.CharField(required=True, write_only=True, trim_whitespace=False)
    password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    default_error_messages = {
        "invalid_token": "Password reset credentials are invalid or expired.",
    }

    def validate(self, attrs):
        password = attrs["password"]
        password_confirm = attrs["password_confirm"]

        if password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": "Password confirmation does not match."}
            )

        user = self._get_user(attrs["uid"])

        if not user.is_active or not default_token_generator.check_token(user, attrs["token"]):
            raise AuthenticationFailed(
                self.error_messages["invalid_token"],
                code="invalid_reset_token",
            )

        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password"])
        user.save(update_fields=["password"])
        return user

    def _get_user(self, uid):
        try:
            decoded_uid = force_str(urlsafe_base64_decode(uid))
            return User.objects.get(pk=decoded_uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoValidationError):
            raise AuthenticationFailed(
                self.error_messages["invalid_token"],
                code="invalid_reset_token",
            )
