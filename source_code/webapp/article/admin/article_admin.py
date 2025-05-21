from article.models import Article
from article.tasks.article_collect_tasks import collect_articles_for_problem_range
from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from problem.models import Problem
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant


class ArticleCollectForm(forms.Form):
    start_id = forms.IntegerField(label="시작 BOJ ID", required=True)
    end_id = forms.IntegerField(label="끝 BOJ ID", required=True)


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ("title", "problem", "source", "created_at")
    search_fields = ("title", "problem__boj_id")
    actions_list = ["collect_articles_by_range"]

    @action(
        description="BOJ ID 범위로 게시글 수집",
        icon="download",
        variant=ActionVariant.PRIMARY,
        url_path="collect-articles",
    )
    def collect_articles_by_range(self, request: HttpRequest, queryset=None):
        form = ArticleCollectForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            start_id = form.cleaned_data["start_id"]
            end_id = form.cleaned_data["end_id"]
            if start_id > end_id:
                messages.error(request, "시작 ID는 끝 ID보다 작아야 합니다.")
                return
            collect_articles_for_problem_range.delay(start_id, end_id)
            messages.success(
                request,
                f"게시글 수집 작업이 시작되었습니다. (ID 범위: {start_id}~{end_id})",
            )
            return redirect(reverse_lazy("admin:article_article_changelist"))
        return render(
            request,
            "admin/collect_articles.html",
            {
                "form": form,
                "title": "BOJ 게시글 수집",
                **self.admin_site.each_context(request),
            },
        )

    collect_articles_by_range.short_description = "BOJ ID 범위로 게시글 수집"
