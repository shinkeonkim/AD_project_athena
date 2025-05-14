from agent.models import QuestionTask, QuestionTaskStatus
from agent.tasks import process_question_task
from api.agent.serializers import QuestionTaskSerializer
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from user.models.ticket import Ticket


class QuestionTaskViewSet(viewsets.ModelViewSet):
    queryset = QuestionTask.objects.all()
    serializer_class = QuestionTaskSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        problem_id = request.data.get("problem_id")
        code = request.data.get("code")
        language = request.data.get("language")
        user = request.user
        ticket, _ = Ticket.objects.get_or_create(user=user)

        if ticket.is_usage_limit_exceeded():
            return Response(
                {"error": "Usage limit exceeded"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not all([problem_id, code, language]):
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            ticket.increase_usage()
            ticket.update_last_used_at()

            task = QuestionTask.objects.create(
                problem_id=problem_id,
                code=code,
                language=language,
                user=user,
            )

        # Start Celery task
        process_question_task.delay(str(task.uuid))

        return Response({"task_uuid": str(task.uuid), "status": task.status})

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def status(self, request, pk=None):
        user = request.user
        task = get_object_or_404(QuestionTask, uuid=pk, user=user)
        return Response(
            {
                "status": task.status,
                "feedback": task.feedback if hasattr(task, "feedback") else None,
                "code_result": (
                    task.code_result if hasattr(task, "code_result") else None
                ),
            }
        )
