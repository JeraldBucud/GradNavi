from django.contrib import admin

from .models import (
    CareerInterest,
    CareerRIASECProfile,
)


@admin.register(CareerInterest)
class CareerInterestAdmin(admin.ModelAdmin):
    list_display = (
        "career",
        "interest",
        "relevance_weight",
        "review_status",
        "source_type",
    )

    list_filter = (
        "review_status",
        "source_type",
        "relevance_weight",
    )

    search_fields = (
        "career__name",
        "interest__name",
    )


@admin.register(CareerRIASECProfile)
class CareerRIASECProfileAdmin(admin.ModelAdmin):
    list_display = (
        "career",
        "dataset",
        "review_status",
    )

    list_filter = (
        "review_status",
        "dataset",
    )

    search_fields = (
        "career__name",
    )
