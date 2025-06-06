from config.models import BaseModel
from django.db import models


class ProblemTestCaseQuerySet(models.QuerySet):
    def official(self):
        return self.filter(is_official=True)


class ProblemTestCase(BaseModel):
    class Meta:
        db_table = "problem_test_cases"

    problem = models.ForeignKey(
        "Problem",
        on_delete=models.CASCADE,
        related_name="test_cases",
        null=True,
        blank=True,
    )
    input_data = models.TextField(null=True, blank=True)
    output_data = models.TextField(null=True, blank=True)
    is_official = models.BooleanField(default=False)

    objects = ProblemTestCaseQuerySet.as_manager()

    def __str__(self):
        return f"TestCase for {self.problem.title}"
