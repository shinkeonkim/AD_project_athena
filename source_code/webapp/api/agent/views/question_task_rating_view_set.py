from agent.models import QuestionTask, QuestionTaskRating
from api.agent.serializers import QuestionTaskRatingSerializer
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class QuestionTaskRatingViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionTaskRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuestionTaskRating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_question_task(self):
        question_task_uuid = self.request.data.get("question_task_uuid")
        if not question_task_uuid:
            raise ValidationError({"question_task_uuid": "This field is required."})

        try:
            return QuestionTask.objects.get(uuid=question_task_uuid)
        except QuestionTask.DoesNotExist:
            raise NotFound("Question task not found.")

    def get_object(self):
        question_task = self.get_question_task()
        obj = QuestionTaskRating.objects.filter(
            user=self.request.user, question_task=question_task
        ).first()
        if not obj:
            raise NotFound("Rating not found.")
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, *args, **kwargs):
        user = request.user
        question_task_uuid = request.data.get("question_task_uuid")
        rating = request.data.get("rating")
        message = request.data.get("message", "")

        # question_task 찾기
        try:
            question_task = QuestionTask.objects.get(uuid=question_task_uuid)
        except QuestionTask.DoesNotExist:
            return Response({"error": "해당 태스크가 존재하지 않습니다."}, status=404)

        # get_or_create로 중복 체크 및 생성
        obj, created = QuestionTaskRating.objects.get_or_create(
            user=user,
            question_task=question_task,
            defaults={"rating": rating, "message": message},
        )
        if not created:
            # 이미 있으면 update
            obj.rating = rating
            obj.message = message
            obj.save()
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # 새로 생성된 경우
            serializer = self.get_serializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
