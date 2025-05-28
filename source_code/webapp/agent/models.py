import uuid

from config.models import BaseModel
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class QuestionTaskStatus(models.TextChoices):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class QuestionTask(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        "user.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    problem = models.ForeignKey("problem.Problem", on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20,
        choices=QuestionTaskStatus.choices,
        default=QuestionTaskStatus.PENDING,
    )
    feedback = models.TextField(null=True, blank=True)
    code_result = models.TextField(null=True, blank=True)


class QuestionTaskRating(BaseModel):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    question_task = models.ForeignKey(
        QuestionTask, on_delete=models.CASCADE, related_name="ratings"
    )
    message = models.TextField(null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ["user", "question_task"]
