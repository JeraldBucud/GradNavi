from django.urls import path

from .views import RecommendationListView


app_name = "careers"

urlpatterns = [
    path(
        "recommendations/",
        RecommendationListView.as_view(),
        name="recommendation-list",
    ),
]
