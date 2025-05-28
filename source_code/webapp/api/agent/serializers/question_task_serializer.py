from agent.models import QuestionTask
from rest_framework import serializers


class QuestionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionTask
        fields = [
            "uuid",
            "problem",
            "code",
            "language",
            "status",
            "feedback",
            "code_result",
        ]
        read_only_fields = ["uuid", "status", "feedback", "code_result"]
