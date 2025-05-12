from config.models import BaseModel
from django.db import models


class ProblemCategory(BaseModel):
    """
    백준 문제의 카테고리 정보를 저장하는 모델
    """

    class Meta:
        db_table = "problem_categories"

    name = models.TextField(null=False, blank=False, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
