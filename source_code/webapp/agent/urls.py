from django.urls import path

from . import views

app_name = "agent"

urlpatterns = [
    path("question", views.question, name="question"),
    path("question/tasks", views.question_task_list, name="question_task_list"),
]
