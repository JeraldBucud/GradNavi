from django.urls import path

from .views import (
    AdminCareerDetailView,
    AdminCareerListCreateView,
    AdminLearningResourceDetailView,
    AdminLearningResourceListCreateView,
    AdminSkillDetailView,
    AdminSkillListCreateView,
    AdminUserDetailView,
    AdminUserListView,
)


urlpatterns = [
    path(
        "users/",
        AdminUserListView.as_view(),
        name="admin-user-list",
    ),
    path(
        "users/<int:pk>/",
        AdminUserDetailView.as_view(),
        name="admin-user-detail",
    ),
    path(
        "careers/",
        AdminCareerListCreateView.as_view(),
        name="admin-career-list",
    ),
    path(
        "careers/<int:pk>/",
        AdminCareerDetailView.as_view(),
        name="admin-career-detail",
    ),
    path(
        "skills/",
        AdminSkillListCreateView.as_view(),
        name="admin-skill-list",
    ),
    path(
        "skills/<int:pk>/",
        AdminSkillDetailView.as_view(),
        name="admin-skill-detail",
    ),
    path(
        "learning-resources/",
        AdminLearningResourceListCreateView.as_view(),
        name="admin-learning-resource-list",
    ),
    path(
        "learning-resources/<int:pk>/",
        AdminLearningResourceDetailView.as_view(),
        name="admin-learning-resource-detail",
    ),
]