from agent.models import QuestionTask, QuestionTaskStatus
from agent.tasks import process_question_task
from api.agent.serializers import QuestionTaskSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class QuestionTaskViewSet(viewsets.ModelViewSet):
    queryset = QuestionTask.objects.all()
    serializer_class = QuestionTaskSerializer
    # TODO: koa - Permission Check

    def create(self, request):
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language")

        if not all([problem_id, code, language]):
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        task = QuestionTask.objects.create(
            problem_id=problem_id, code=code, language=language
        )

        # Start Celery task
        process_question_task.delay(str(task.uuid))

        return Response({"task_uuid": str(task.uuid), "status": task.status})

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        task = get_object_or_404(QuestionTask, uuid=pk)
        return Response(
            {
                "status": task.status,
                "feedback": task.feedback if hasattr(task, "feedback") else None,
                "code_result": (
                    task.code_result if hasattr(task, "code_result") else None
                ),
            }
        )
