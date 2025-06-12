from django.contrib import admin
from problem.models import ProblemTestCase
from unfold.admin import ModelAdmin


@admin.register(ProblemTestCase)
class ProblemTestCaseAdmin(ModelAdmin):
    list_display = (
        "problem",
        "input_data",
        "output_data",
        "is_official",
        "created_at",
        "updated_at",
    )
    search_fields = ("problem__title", "problem__boj_id")
    list_filter = ("is_official",)
    ordering = ("-created_at",)
    list_per_page = 20
    list_max_show_all = 20
    list_editable = ("is_official",)
    list_display_links = ("problem", "input_data", "output_data")
    list_select_related = ("problem",)
