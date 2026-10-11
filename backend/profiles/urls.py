from django.urls import path

from .views import (
    CareerReferenceView,
    InterestReferenceView,
    SkillReferenceView,
    StudentProfileView,
)


app_name = "profiles"

urlpatterns = [
    path(
        "profile/",
        StudentProfileView.as_view(),
        name="profile-detail",
    ),
    path(
        "profile/reference/skills/",
        SkillReferenceView.as_view(),
        name="profile-reference-skills",
    ),
    path(
        "profile/reference/interests/",
        InterestReferenceView.as_view(),
        name="profile-reference-interests",
    ),
    path(
        "profile/reference/careers/",
        CareerReferenceView.as_view(),
        name="profile-reference-careers",
    ),
]
