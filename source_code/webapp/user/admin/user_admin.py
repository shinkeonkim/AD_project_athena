from django.contrib import admin
from user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "username",
        "is_active",
        "is_staff",
        "created_at",
        "updated_at",
    )
    search_fields = ("email", "username")
    list_filter = ("is_active", "is_staff")
    ordering = ("-created_at",)
    list_per_page = 20
