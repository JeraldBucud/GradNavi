from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, RegistrationView


app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegistrationView.as_view(), name="register"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
