from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from gradnavi.exceptions import ConflictError


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
        return User.objects.create_user(password=password, **validated_data)


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role")
        read_only_fields = fields


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
