from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import path, reverse_lazy
from problem.models import Problem
from problem.tasks.problem_collect_tasks import collect_problem_range
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant
from unfold.widgets import UnfoldAdminTextInputWidget


class ProblemCollectForm(forms.Form):
    start_id = forms.IntegerField(
        label="시작 ID", widget=UnfoldAdminTextInputWidget, required=True
    )
    end_id = forms.IntegerField(
        label="끝 ID", widget=UnfoldAdminTextInputWidget, required=True
    )


@admin.register(Problem)
class ProblemAdmin(ModelAdmin):
    list_display = ("boj_id", "title", "level")
    search_fields = ("boj_id", "title")
    list_filter = ("level",)

    actions_list = ["collect_problems_by_range"]

    @action(
        description="BOJ ID 범위로 문제 수집",
        icon="download",
        variant=ActionVariant.PRIMARY,
        url_path="collect-problems",
    )
    def collect_problems_by_range(
        self, request: HttpRequest, queryset: QuerySet = None
    ):
        form = ProblemCollectForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            start_id = form.cleaned_data["start_id"]
            end_id = form.cleaned_data["end_id"]

            if start_id > end_id:
                messages.error(request, "시작 ID는 끝 ID보다 작아야 합니다.")
                return self.response_action(request)

            # Celery task 실행
            collect_problem_range.delay(start_id, end_id)
            messages.success(
                request,
                f"문제 수집 작업이 시작되었습니다. (ID 범위: {start_id}~{end_id})",
            )
            return redirect(reverse_lazy("admin:problem_problem_changelist"))

        return render(
            request,
            "admin/collect_problems.html",
            {
                "form": form,
                "title": "BOJ 문제 수집",
                **self.admin_site.each_context(request),
            },
        )
