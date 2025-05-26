from django.db.transaction import atomic
from django.db.utils import IntegrityError
from django.test import TestCase
from problem.models import Problem, ProblemCategory


class ProblemModelTest(TestCase):
    def setUp(self):
        self.problem_data = {
            "boj_id": 1000,
            "title": "A+B",
            "description": "두 정수 A와 B를 입력받아 A+B를 출력하는 프로그램을 작성하시오.",
            "input_description": "첫째 줄에 A와 B가 주어진다. (0 < A, B < 10)",
            "output_description": "첫째 줄에 A+B를 출력한다.",
            "level": 1,
        }
        self.category = ProblemCategory.objects.create(
            name="수학", description="수학 관련 문제"
        )

    def test_create_problem(self):
        """문제 생성 테스트"""
        problem = Problem.objects.create(**self.problem_data)
        self.assertEqual(problem.boj_id, self.problem_data["boj_id"])
        self.assertEqual(problem.title, self.problem_data["title"])
        self.assertEqual(problem.description, self.problem_data["description"])
        self.assertEqual(
            problem.input_description, self.problem_data["input_description"]
        )
        self.assertEqual(
            problem.output_description, self.problem_data["output_description"]
        )
        self.assertEqual(problem.level, self.problem_data["level"])

    def test_problem_str(self):
        """Problem 모델의 문자열 표현 테스트"""
        problem = Problem.objects.create(**self.problem_data)
        self.assertEqual(
            str(problem),
            f"[{self.problem_data['boj_id']}] {self.problem_data['title']}",
        )

    def test_unique_boj_id(self):
        """중복된 boj_id 방지 테스트"""
        Problem.objects.create(**self.problem_data)
        with self.assertRaises(IntegrityError):
            Problem.objects.create(**self.problem_data)

    def test_required_boj_id(self):
        """boj_id 필수 필드 검증 테스트"""
        with self.assertRaises(IntegrityError):
            Problem.objects.create(
                title="Test Problem",
                description="Test Description",
                input_description="Test Input",
                output_description="Test Output",
                level=1,
            )

    def test_required_title(self):
        """title 필수 필드 검증 테스트"""
        with self.assertRaises(IntegrityError):
            with atomic():
                Problem.objects.create(
                    boj_id=1001,
                    title=None,
                    description="Test Description",
                    input_description="Test Input",
                    output_description="Test Output",
                    level=1,
                )

    def test_required_input_description(self):
        """input_description 필수 필드 검증 테스트"""
        with self.assertRaises(IntegrityError):
            with atomic():
                Problem.objects.create(
                    boj_id=1001,
                    title="Test Problem",
                    description="Test Description",
                    input_description=None,
                    output_description="Test Output",
                    level=1,
                )

    def test_required_output_description(self):
        """output_description 필수 필드 검증 테스트"""
        with self.assertRaises(IntegrityError):
            with atomic():
                Problem.objects.create(
                    boj_id=1001,
                    title="Test Problem",
                    description="Test Description",
                    input_description="Test Input",
                    output_description=None,
                    level=1,
                )

    def test_default_level(self):
        """level 기본값 테스트"""
        problem = Problem.objects.create(
            boj_id=1001,
            title="Test Problem",
            description="Test Description",
            input_description="Test Input",
            output_description="Test Output",
        )
        self.assertEqual(problem.level, 0)  # 기본값 확인

    def test_problem_categories(self):
        """문제 카테고리 관계 테스트"""
        problem = Problem.objects.create(**self.problem_data)
        problem.categories.add(self.category)
        self.assertEqual(problem.categories.count(), 1)
        self.assertEqual(problem.categories.first(), self.category)
        self.assertEqual(self.category.problems.count(), 1)
        self.assertEqual(self.category.problems.first(), problem)

    def test_extra_information(self):
        """추가 정보 필드 테스트"""
        extra_info = {
            "time_limit": "1초",
            "memory_limit": "128MB",
            "submission_count": 1000,
        }
        problem = Problem.objects.create(
            **self.problem_data, extra_information=extra_info
        )
        self.assertEqual(problem.extra_information, extra_info)
