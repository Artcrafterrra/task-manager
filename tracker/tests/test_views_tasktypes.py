from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from tracker.models import TaskType, Position

User = get_user_model()


class TestTaskTypeViews(TestCase):
    def setUp(self):
        self.pos = Position.objects.create(name="Support")
        self.user = User.objects.create_user(username="user", password="pass12345", position=self.pos)
        TaskType.objects.create(name="Bug")
        TaskType.objects.create(name="Feature")
        TaskType.objects.create(name="Ops")

    def test_list_requires_login(self):
        url = reverse("tracker:tasktype-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_list_basic(self):
        self.client.login(username="user", password="pass12345")
        url = reverse("tracker:tasktype-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("types", resp.context)
        names = [t.name for t in resp.context["types"]]
        self.assertEqual(sorted(names), ["Bug", "Feature", "Ops"])

    def test_create_valid(self):
        self.client.login(username="user", password="pass12345")
        url = reverse("tracker:tasktype-create")
        resp = self.client.post(url, {"name": "Docs"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(TaskType.objects.filter(name="Docs").exists())

    def test_create_duplicate_validation(self):
        self.client.login(username="user", password="pass12345")
        url = reverse("tracker:tasktype-create")
        resp = self.client.post(url, {"name": "bug"})
        self.assertEqual(resp.status_code, 200)
        form = resp.context["form"]
        self.assertTrue(form.is_bound)
        self.assertIn("name", form.errors)
        self.assertIn("Such task type already exists.", form.errors["name"])

