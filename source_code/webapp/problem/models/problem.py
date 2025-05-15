from config.models import BaseModel
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class Problem(BaseModel):
    """
    수집된 백준 문제 정보를 저장하는 모델
    """

    class Meta:
        db_table = "problems"
        indexes = [
            models.Index(fields=["boj_id"]),
            models.Index(fields=["title"]),
            models.Index(fields=["level"]),
            GinIndex(
                fields=["title"],
                name="problems_title_gin_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    boj_id = models.IntegerField(unique=True, null=False, blank=False)
    title = models.TextField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    input_description = models.TextField(null=False, blank=False)
    output_description = models.TextField(null=False, blank=False)
    extra_information = models.JSONField(null=True, blank=True)
    level = models.IntegerField(null=False, blank=False, default=0)

    categories = models.ManyToManyField(
        "ProblemCategory", related_name="problems", blank=True
    )

    def __str__(self):
        return f"[{self.boj_id}] {self.title}"
