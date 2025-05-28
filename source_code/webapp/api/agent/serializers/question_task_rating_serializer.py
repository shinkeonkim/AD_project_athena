from agent.models import QuestionTask, QuestionTaskRating
from rest_framework import serializers


class QuestionTaskRatingSerializer(serializers.ModelSerializer):
    question_task_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = QuestionTaskRating
        fields = ["id", "user", "question_task_uuid", "message", "rating", "created_at"]
        read_only_fields = ["user", "created_at"]

    def create(self, validated_data):
        question_task_uuid = validated_data.pop("question_task_uuid")
        question_task = QuestionTask.objects.get(uuid=question_task_uuid)
        validated_data["question_task"] = question_task
        return super().create(validated_data)
