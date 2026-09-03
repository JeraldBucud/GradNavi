from django.urls import path

from .views import (
    LearningSuggestionListView,
    RecommendationListView,
    RoadmapListView,
)


app_name = "careers"

urlpatterns = [
    path(
        "recommendations/",
        RecommendationListView.as_view(),
        name="recommendation-list",
    ),
    path(
        "learning-resources/",
        LearningSuggestionListView.as_view(),
        name="learning-resource-suggestions",
    ),
    path(
        "roadmaps/",
        RoadmapListView.as_view(),
        name="roadmap-list",
    ),
]
