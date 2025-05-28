import logging

from article.exceptions import InvalidProblemRangeException
from article.models import Article
from article.tasks.article_collect_tasks import collect_articles_for_problem_range
from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant

logger = logging.getLogger(__name__)


class ArticleCollectForm(forms.Form):
    start_id = forms.IntegerField(label="시작 BOJ ID", required=True)
    end_id = forms.IntegerField(label="끝 BOJ ID", required=True)


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = (
        "title",
        "problem",
        "source",
        "author",
        "relevance_confidence",
        "created_at",
        "updated_at",
        "view_article",
    )
    list_filter = ("source", "problem", "created_at", "updated_at")
    search_fields = ("title", "content", "author", "problem__title")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    actions_list = ["collect_articles_by_range"]

    def view_article(self, obj):
        if obj.full_url:
            return format_html(
                '<a href="{}" target="_blank">View Article</a>', obj.full_url
            )
        return "-"

    view_article.short_description = "View Article"

    @action(
        description="BOJ ID 범위로 게시글 수집",
        icon="download",
        variant=ActionVariant.PRIMARY,
        url_path="collect-articles",
    )
    def collect_articles_by_range(self, request: HttpRequest, queryset=None):
        form = ArticleCollectForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            try:
                start_id = form.cleaned_data["start_id"]
                end_id = form.cleaned_data["end_id"]

                if start_id <= 0:
                    raise InvalidProblemRangeException(
                        "시작 ID는 0보다 커야 합니다", {"start_id": start_id}
                    )
                if end_id < start_id:
                    raise InvalidProblemRangeException(
                        "끝 ID는 시작 ID보다 크거나 같아야 합니다",
                        {"start_id": start_id, "end_id": end_id},
                    )

                collect_articles_for_problem_range.delay(start_id, end_id)
                messages.success(
                    request,
                    f"문제 {start_id}부터 {end_id}까지의 게시글 수집이 시작되었습니다",
                )
                return redirect(reverse_lazy("admin:article_article_changelist"))
            except InvalidProblemRangeException as e:
                messages.error(request, e.message)
                if hasattr(e, "data"):
                    logger.error(f"Validation error data: {e.data}")
            except ValueError:
                messages.error(request, "올바른 숫자를 입력해주세요")

        return render(
            request,
            "admin/collect_articles.html",
            {
                "form": form,
                "title": "BOJ 게시글 수집",
                **self.admin_site.each_context(request),
            },
        )
