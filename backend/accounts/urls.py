from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AccountSettingsView,
    CurrentUserView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PasswordChangeView,
    ProfilePhotoView,
    RegistrationView,
)


app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path(
        "settings/",
        AccountSettingsView.as_view(),
        name="settings",
    ),
    path(
        "settings/profile-photo/",
        ProfilePhotoView.as_view(),
        name="profile-photo",
    ),
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="password-change",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", CurrentUserView.as_view(), name="me"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("register/", RegistrationView.as_view(), name="register"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
