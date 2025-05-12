from config.models import BaseModel
from django.db import models
from problem.models import Problem


class Article(BaseModel):
    """
    백준 문제와 관련된 글 / 게시글 등을 수집하여 저장하는 모델
    """

    class Meta:
        db_table = "articles"

    title = models.TextField()
    content = models.TextField()

    full_url = models.URLField(null=True, blank=True)
    site_url = models.URLField(null=True, blank=True)

    author = models.TextField()
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="articles"
    )
