"""
URL configuration for GradNavi interview preparation.

WBS 6.6 exposes authenticated interview question
generation and interview feedback operations.
"""

from django.urls import path

from interviews.views import (
    InterviewFeedbackGenerationView,
    InterviewQuestionGenerationView,
)


app_name = "interviews"

urlpatterns = [
    path(
        "interviews/questions/",
        InterviewQuestionGenerationView.as_view(),
        name="question-generate",
    ),
    path(
        "interviews/feedback/",
        InterviewFeedbackGenerationView.as_view(),
        name="feedback-generate",
    ),
]