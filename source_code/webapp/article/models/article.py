from config.models import BaseModel
from django.db import models
from problem.models import Problem


class Article(BaseModel):
    """
    백준 문제와 관련된 글 / 게시글 등을 수집하여 저장하는 모델
    """

    class Meta:
        db_table = "articles"

    # Basic article information
    title = models.TextField()
    author = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=64, null=True, blank=True)

    # URLs
    full_url = models.URLField(null=True, blank=True)
    site_url = models.URLField(null=True, blank=True)

    # Problem relationship
    problem = models.ForeignKey(
        Problem, on_delete=models.CASCADE, related_name="articles"
    )

    # Structured content
    summary = models.TextField(null=True, blank=True)
    approach = models.TextField(null=True, blank=True)
    complexity_analysis = models.TextField(null=True, blank=True)
    additional_tips = models.TextField(null=True, blank=True)
    code_blocks = models.JSONField(null=True, blank=True)

    # Metadata
    relevance_confidence = models.FloatField(null=True, blank=True)
