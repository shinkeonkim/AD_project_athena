from django.contrib import admin
from problem.models import ProblemTestCase
from unfold.admin import ModelAdmin


@admin.register(ProblemTestCase)
class ProblemTestCaseAdmin(ModelAdmin):
    list_display = ("problem", "input_data", "output_data")
    search_fields = ("problem__title",)
