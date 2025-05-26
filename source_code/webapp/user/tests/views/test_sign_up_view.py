from django.test import Client, TestCase
from django.urls import reverse
from user.models import User


class SignUpViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse("user:signup")

    def test_get_signup_page(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/signup.html")
        self.assertIn("form", response.context)

    def test_signup_success(self):
        response = self.client.post(
            self.signup_url,
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "newpass123",
                "password2": "newpass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("user:signin"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_invalid_data(self):
        response = self.client.post(
            self.signup_url,
            {
                "username": "newuser",
                "email": "invalid-email",
                "password1": "newpass123",
                "password2": "differentpass",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/signup.html")
        self.assertIn("form", response.context)
        self.assertFalse(User.objects.filter(username="newuser").exists())
