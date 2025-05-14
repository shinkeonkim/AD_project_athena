from django.contrib import admin
from unfold.admin import ModelAdmin
from user.models.ticket import Ticket


@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = (
        "user",
        "usage_per_day",
        "usage_per_month",
        "usage_per_year",
        "usage_per_lifetime",
    )
    list_filter = ("user",)
    search_fields = ("user__email", "user__username")
    ordering = ("-created_at",)
    list_per_page = 20
