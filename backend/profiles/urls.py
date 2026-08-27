from django.urls import path

from .views import StudentProfileView


app_name = "profiles"

urlpatterns = [
    path("profile/", StudentProfileView.as_view(), name="profile-detail"),
]
