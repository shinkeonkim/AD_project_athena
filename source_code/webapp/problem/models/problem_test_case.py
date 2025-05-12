from config.models import BaseModel
from django.db import models


class ProblemTestCase(BaseModel):
    class Meta:
        db_table = "problem_test_cases"

    problem = models.ForeignKey(
        "Problem", on_delete=models.CASCADE, related_name="test_cases"
    )
    input_data = models.TextField()
    output_data = models.TextField()

    def __str__(self):
        return f"TestCase for {self.problem.title}"
