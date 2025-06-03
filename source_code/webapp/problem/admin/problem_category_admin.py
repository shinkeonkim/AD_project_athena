from django.contrib import admin
from problem.models import ProblemCategory
from unfold.admin import ModelAdmin


@admin.register(ProblemCategory)
class ProblemCategoryAdmin(ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
