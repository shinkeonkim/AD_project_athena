from django.test import Client, TestCase
from django.urls import reverse
from user.models import User


class SignInViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signin_url = reverse("user:signin")
        self.test_user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_get_signin_page(self):
        response = self.client.get(self.signin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/signin.html")
        self.assertIn("form", response.context)

    def test_signin_success(self):
        response = self.client.post(
            self.signin_url, {"email": "test@example.com", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("main:index"))

    def test_signin_invalid_credentials(self):
        response = self.client.post(
            self.signin_url, {"email": "test@example.com", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/signin.html")
        self.assertIn("login_error", response.context)
