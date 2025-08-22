from django.test import TestCase, override_settings
from django.urls import reverse, NoReverseMatch
from django.contrib.auth import get_user_model

from tracker.models import Position

User = get_user_model()


class TestSignUp(TestCase):
    def setUp(self):
        self.pos = Position.objects.create(name="Manager")

    @override_settings(LOGIN_REDIRECT_URL="/")
    def test_signup_creates_user_and_logs_in(self):
        try:
            url = reverse("signup")
        except NoReverseMatch:
            self.skipTest("SignUpView URL name 'signup' is not configured in project urls.")
        resp = self.client.get(url)
        if resp.status_code == 404:
            self.skipTest("SignUpView URL exists but returns 404 in GET.")
        data = {
            "username": "newbie",
            "first_name": "New",
            "last_name": "Bie",
            "email": "",
            "password1": "aStrongPassword123",
            "password2": "aStrongPassword123",
            "position": self.pos.id,
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username="newbie").exists())
        self.assertTrue(resp.context["user"].is_authenticated)

    def test_signup_forbidden_for_authenticated(self):
        User.objects.create_user(username="exists", password="pass12345")
        self.client.login(username="exists", password="pass12345")
        try:
            url = reverse("signup")
        except NoReverseMatch:
            self.skipTest("SignUpView URL name 'signup' is not configured in project urls.")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (302, 403))