from django.contrib import admin
from unfold.admin import ModelAdmin
from user.models.ticket import Ticket


@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = (
        "user",
        "plan_type",
        "usage_per_day",
        "max_usage_per_day",
        "usage_per_month",
        "max_usage_per_month",
        "usage_per_year",
        "max_usage_per_year",
        "usage_per_lifetime",
        "max_usage_per_lifetime",
    )
    list_filter = ("user", "plan_type")
    search_fields = ("user__email", "user__username")
    ordering = ("-created_at",)
    list_per_page = 20

    readonly_fields = (
        "user",
        "usage_per_day",
        "usage_per_month",
        "usage_per_year",
        "usage_per_lifetime",
        "last_used_at",
    )

    fieldsets = (
        (
            "User Information",
            {
                "fields": ("user", "plan_type"),
            },
        ),
        (
            "Daily Usage",
            {
                "fields": (
                    "usage_per_day",
                    "max_usage_per_day",
                ),
            },
        ),
        (
            "Monthly Usage",
            {
                "fields": (
                    "usage_per_month",
                    "max_usage_per_month",
                ),
            },
        ),
        (
            "Yearly Usage",
            {
                "fields": (
                    "usage_per_year",
                    "max_usage_per_year",
                ),
            },
        ),
        (
            "Lifetime Usage",
            {
                "fields": (
                    "usage_per_lifetime",
                    "max_usage_per_lifetime",
                ),
            },
        ),
        (
            "Last Used",
            {
                "fields": ("last_used_at",),
            },
        ),
    )
