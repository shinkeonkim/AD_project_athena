from config.models import BaseModel
from django.db import models
from problem.models.problem import Problem


class ProblemCode(BaseModel):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    solution_code = models.TextField(null=False, blank=False)
    validation_code = models.TextField(null=False, blank=False)
    language = models.CharField(
        max_length=20, null=False, blank=False, default="python"
    )

    class Meta:
        db_table = "problem_codes"
