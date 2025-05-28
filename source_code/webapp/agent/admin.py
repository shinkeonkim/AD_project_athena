from agent.models import QuestionTaskRating
from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import QuestionTask


@admin.register(QuestionTask)
class QuestionTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "problem", "status", "created_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("problem__title",)
    list_per_page = 20


@admin.register(QuestionTaskRating)
class QuestionTaskRatingAdmin(ModelAdmin):
    list_display = ["id", "user", "question_task", "rating", "message", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["user__username", "message"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "question_task")
