from django.urls import path

from .views import (
    ExploreCareerDetailView,
    ExploreCareerEvaluateView,
    ExploreCareerListView,
    GuidanceCareerListView,
    JobDescriptionMatchView,
    LearningResourceFeedbackView,
    LearningResourceRecommendationView,
    LearningResourceReportCreateView,
    LearningSuggestionListView,
    RecommendationListView,
    RoadmapListView,
    RoadmapOverviewView,
    RoadmapProgressCompleteView,
    RoadmapProgressStartView,
    SelectedCareerReadinessView,
    SkillGapSummaryView,
    TopMatchExplanationView,
)


app_name = "careers"

urlpatterns = [
    path(
        "careers/job-match/",
        JobDescriptionMatchView.as_view(),
        name="job-description-match",
    ),
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
    ),    path(
        "roadmap-overview/",
        RoadmapOverviewView.as_view(),
        name="roadmap-overview",
    ),
    path(
        "roadmap-progress/start/",
        RoadmapProgressStartView.as_view(),
        name="roadmap-progress-start",
    ),
    path(
        "roadmap-progress/complete/",
        RoadmapProgressCompleteView.as_view(),
        name="roadmap-progress-complete",
    ),
    path(
        "learning-resource-recommendations/",
        LearningResourceRecommendationView.as_view(),
        name="learning-resource-recommendations",
    ),
    path(
        "learning-resource-feedback/<int:resource_id>/",
        LearningResourceFeedbackView.as_view(),
        name="learning-resource-feedback",
    ),
    path(
        "learning-resource-reports/",
        LearningResourceReportCreateView.as_view(),
        name="learning-resource-reports",
    ),


    path(
        "explore-careers/",
        ExploreCareerListView.as_view(),
        name="explore-career-list",
    ),
    path(
        "explore-careers/<int:career_id>/",
        ExploreCareerDetailView.as_view(),
        name="explore-career-detail",
    ),
    path(
        "explore-careers/<int:career_id>/evaluate/",
        ExploreCareerEvaluateView.as_view(),
        name="explore-career-evaluate",
    ),
    path(
        "guidance-careers/",
        GuidanceCareerListView.as_view(),
        name="guidance-career-list",
    ),
]
