from django.urls import path

from .views import (
    LearningSuggestionListView,
    RecommendationListView,
    SelectedCareerReadinessView,
    SkillGapSummaryView,
    RoadmapListView,
    TopMatchExplanationView,
)


app_name = "careers"

urlpatterns = [
    path(
        "recommendations/",
        RecommendationListView.as_view(),
        name="recommendation-list",
    ),
    path(
        "recommendations/top-explanation/",
        TopMatchExplanationView.as_view(),
        name="top-match-explanation",
    ),
    path(
        "skill-gap-summary/",
        SkillGapSummaryView.as_view(),
        name="skill-gap-summary",
    ),
    path(
        "readiness/",
        SelectedCareerReadinessView.as_view(),
        name="selected-career-readiness",
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
