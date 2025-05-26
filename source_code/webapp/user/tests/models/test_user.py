from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from user.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        }

    def test_create_user(self):
        """일반 사용자 생성 테스트"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.username, self.user_data["username"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """슈퍼유저 생성 테스트"""
        superuser = User.objects.create_superuser(
            email="admin@example.com", username="admin", password="adminpass123"
        )
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_str(self):
        """User 모델의 문자열 표현 테스트"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data["email"])

    def test_unique_username(self):
        """중복된 username 방지 테스트"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="another@example.com", username="testuser", password="testpass123"
            )

    def test_unique_email(self):
        """중복된 email 방지 테스트"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="test@example.com", username="anotheruser", password="testpass123"
            )

    def test_required_fields(self):
        """필수 필드 검증 테스트"""
        # email이 없는 경우
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="", username="testuser", password="testpass123"
            )

        # email이 None인 경우
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None, username="testuser", password="testpass123"
            )

        # username이 None인 경우
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="test@example.com", username=None, password="testpass123"
            )

    def test_password_validation(self):
        """비밀번호 검증 테스트"""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.check_password("wrongpassword"))

    def test_user_creation_without_password(self):
        """비밀번호 없이 사용자 생성 테스트"""
        user = User.objects.create_user(email="nopass@example.com", username="nopass")
        self.assertFalse(user.has_usable_password())

    def test_email_normalization(self):
        """이메일 정규화 테스트"""
        user = User.objects.create_user(
            email="Test.User@Example.com", username="testuser", password="testpass123"
        )
        self.assertEqual(user.email, "Test.User@example.com")
