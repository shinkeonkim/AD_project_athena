from django.db.transaction import atomic
from django.db.utils import IntegrityError
from django.test import TestCase
from problem.models import Problem, ProblemTestCase


class ProblemTestCaseModelTest(TestCase):
    def setUp(self):
        self.problem = Problem.objects.create(
            boj_id=1000,
            title="A+B",
            input_description="Test Input",
            output_description="Test Output",
        )
        self.test_case_data = {
            "problem": self.problem,
            "input_data": "1 2",
            "output_data": "3",
        }

    def test_create_test_case(self):
        """테스트 케이스 생성 테스트"""
        test_case = ProblemTestCase.objects.create(**self.test_case_data)
        self.assertEqual(test_case.problem, self.problem)
        self.assertEqual(test_case.input_data, self.test_case_data["input_data"])
        self.assertEqual(test_case.output_data, self.test_case_data["output_data"])

    def test_test_case_str(self):
        """ProblemTestCase 모델의 문자열 표현 테스트"""
        test_case = ProblemTestCase.objects.create(**self.test_case_data)
        self.assertEqual(str(test_case), f"TestCase for {self.problem.title}")

    def test_problem_relationship(self):
        """문제와의 관계 테스트"""
        test_case = ProblemTestCase.objects.create(**self.test_case_data)
        self.assertEqual(test_case.problem, self.problem)
        self.assertEqual(self.problem.test_cases.count(), 1)
        self.assertEqual(self.problem.test_cases.first(), test_case)
