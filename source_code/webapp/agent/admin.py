from django.contrib import admin

from .models import QuestionTask


@admin.register(QuestionTask)
class QuestionTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "problem", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("problem__title",)
    list_per_page = 20
