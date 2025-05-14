from datetime import timedelta

from config.models import BaseModel
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from user.models.user import User


class Ticket(BaseModel):
    class Meta:
        db_table = "tickets"
        verbose_name = _("ticket")
        verbose_name_plural = _("tickets")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ticket")
    max_usage_per_day = models.PositiveIntegerField(default=50)
    max_usage_per_month = models.PositiveIntegerField(default=5000)
    max_usage_per_year = models.PositiveIntegerField(default=50000)
    max_usage_per_lifetime = models.PositiveIntegerField(default=500000)

    usage_per_day = models.IntegerField(default=0)
    usage_per_month = models.IntegerField(default=0)
    usage_per_year = models.IntegerField(default=0)
    usage_per_lifetime = models.IntegerField(default=0)

    last_used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.id}"

    def is_last_used_one_day_ago(self):
        """한국 기준 00:00:00 기준으로 하루 전인지 확인"""
        if not self.last_used_at:
            return True

        return self.last_used_at < timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=1)

    def is_last_used_one_month_ago(self):
        """한국 기준 00:00:00 기준으로 한달 전인지 확인"""
        if not self.last_used_at:
            return True

        return self.last_used_at < timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=31)

    def is_last_used_one_year_ago(self):
        """한국 기준 00:00:00 기준으로 일년 전인지 확인"""
        if not self.last_used_at:
            return True

        return self.last_used_at < timezone.now().replace(
            hour=0, minute=0, second=0
        ) - timedelta(days=365)

    def reset_usage_per_day(self):
        if self.is_last_used_one_day_ago():
            self.usage_per_day = 0
            self.save()

    def reset_usage_per_month(self):
        if self.is_last_used_one_month_ago():
            self.usage_per_month = 0
            self.save()

    def reset_usage_per_year(self):
        if self.is_last_used_one_year_ago():
            self.usage_per_year = 0
            self.save()

    def reset_usage(self):
        self.reset_usage_per_day()
        self.reset_usage_per_month()
        self.reset_usage_per_year()

    def update_usage(self, amount):
        self.reset_usage()
        self.usage_per_day += amount
        self.usage_per_month += amount
        self.usage_per_year += amount
        self.usage_per_lifetime += amount
        self.save()

    def increase_usage(self):
        self.update_usage(1)

    def decrease_usage(self):
        self.update_usage(-1)

    def update_last_used_at(self):
        self.last_used_at = timezone.now()
        self.save()

    def is_usage_limit_exceeded(self):
        self.reset_usage()

        return (
            self.usage_per_day >= self.max_usage_per_day
            or self.usage_per_month >= self.max_usage_per_month
            or self.usage_per_year >= self.max_usage_per_year
            or self.usage_per_lifetime >= self.max_usage_per_lifetime
        )
