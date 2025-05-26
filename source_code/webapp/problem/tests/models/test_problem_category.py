from django.db.transaction import atomic
from django.db.utils import IntegrityError
from django.test import TestCase
from problem.models import ProblemCategory


class ProblemCategoryModelTest(TestCase):
    def setUp(self):
        self.category_data = {"name": "수학", "description": "수학 관련 문제"}

    def test_create_category(self):
        """카테고리 생성 테스트"""
        category = ProblemCategory.objects.create(**self.category_data)
        self.assertEqual(category.name, self.category_data["name"])
        self.assertEqual(category.description, self.category_data["description"])

    def test_category_str(self):
        """ProblemCategory 모델의 문자열 표현 테스트"""
        category = ProblemCategory.objects.create(**self.category_data)
        self.assertEqual(str(category), self.category_data["name"])

    def test_unique_name(self):
        """중복된 name 방지 테스트"""
        ProblemCategory.objects.create(**self.category_data)
        with self.assertRaises(IntegrityError):
            with atomic():
                ProblemCategory.objects.create(**self.category_data)

    def test_required_fields(self):
        """필수 필드 검증 테스트"""
        # name이 없는 경우
        with self.assertRaises(IntegrityError):
            ProblemCategory.objects.create(description="Test Description")

        # name이 빈 문자열인 경우
        with self.assertRaises(IntegrityError):
            with atomic():
                ProblemCategory.objects.create(name="", description="Test Description")

    def test_optional_description(self):
        """선택적 description 필드 테스트"""
        category = ProblemCategory.objects.create(name="알고리즘")
        self.assertIsNone(category.description)
