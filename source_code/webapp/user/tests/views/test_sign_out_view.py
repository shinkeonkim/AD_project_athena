from django.test import Client, TestCase
from django.urls import reverse
from user.models import User


class SignOutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signout_url = reverse("user:signout")
        self.test_user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_signout_when_logged_in(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.signout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("user:signin"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_signout_when_not_logged_in(self):
        response = self.client.get(self.signout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("user:signin"))
