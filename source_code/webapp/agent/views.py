from agent.models import QuestionTask
from django.core.paginator import Paginator
from django.shortcuts import redirect, render


def question(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "agent/question.html")


def question_task_list(request):
    if not request.user.is_authenticated:
        return redirect("login")

    question_tasks = QuestionTask.objects.filter(user=request.user).order_by(
        "-created_at"
    )

    paginator = Paginator(question_tasks, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "current_page": "질문 기록",
        "page_obj": page_obj,
    }

    return render(request, "agent/question_task_list.html", context)
