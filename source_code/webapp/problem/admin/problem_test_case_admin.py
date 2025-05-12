from django.contrib import admin
from problem.models import ProblemTestCase


@admin.register(ProblemTestCase)
class ProblemTestCaseAdmin(admin.ModelAdmin):
    list_display = ("problem", "input_data", "output_data")
    search_fields = ("problem__title",)
