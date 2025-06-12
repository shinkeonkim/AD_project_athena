from django.contrib import admin
from problem.models import ProblemCode
from unfold.admin import ModelAdmin


@admin.register(ProblemCode)
class ProblemCodeAdmin(ModelAdmin):
    list_display = (
        "problem",
        "solution_code",
        "validation_code",
        "language",
        "created_at",
        "updated_at",
    )
    search_fields = ("problem__title", "problem__boj_id")
    list_filter = ("language",)
    ordering = ("-created_at",)
