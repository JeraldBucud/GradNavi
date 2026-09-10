from django.urls import path

from .views import ResumeGenerationView


app_name = "documents"

urlpatterns = [
    path(
        "documents/resume/generate/",
        ResumeGenerationView.as_view(),
        name="resume-generate",
    ),
]

