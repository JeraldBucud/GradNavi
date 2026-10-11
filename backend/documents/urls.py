from django.urls import path

from .views import CoverLetterGenerationView, ResumeGenerationView


app_name = "documents"

urlpatterns = [
    path(
        "documents/cover-letter/generate/",
        CoverLetterGenerationView.as_view(),
        name="cover-letter-generate",
    ),
    path(
        "documents/resume/generate/",
        ResumeGenerationView.as_view(),
        name="resume-generate",
    ),
]

