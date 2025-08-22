from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

from tracker.models import Task, TaskType, Position

User = get_user_model()


class TestTaskViews(TestCase):
    def setUp(self):
        self.pos = Position.objects.create(name="Dev")
        self.user = User.objects.create_user(username="u1", password="pass12345", position=self.pos)
        self.other = User.objects.create_user(username="u2", password="pass12345", position=self.pos)
        self.task_type = TaskType.objects.create(name="Bug")

        self.task1 = Task.objects.create(
            name="T1", task_type=self.task_type, creator=self.user, is_completed=False, priority="medium"
        )
        self.task1.assignees.add(self.user)

        self.task2 = Task.objects.create(
            name="T2", task_type=self.task_type, creator=self.user, is_completed=True, priority="high"
        )
        self.task2.assignees.add(self.other)

        self.task3 = Task.objects.create(
            name="T3",
            task_type=self.task_type,
            creator=self.other,
            is_completed=False,
            priority="low",
            deadline=timezone.localdate() + datetime.timedelta(days=1),
        )
        self.task3.assignees.add(self.user)

    def test_task_list_requires_login(self):
        url = reverse("tracker:task-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_task_list_filters(self):
        self.client.login(username="u1", password="pass12345")
        base = reverse("tracker:task-list")

        resp = self.client.get(base)
        self.assertEqual(resp.status_code, 200)
        self.assertCountEqual(resp.context["object_list"], [self.task1, self.task2, self.task3])

        resp = self.client.get(base, {"my": "1"})
        self.assertCountEqual(resp.context["object_list"], [self.task1, self.task3])

        resp = self.client.get(base, {"created": "1"})
        self.assertCountEqual(resp.context["object_list"], [self.task1, self.task2])

        resp = self.client.get(base, {"done": "1"})
        self.assertCountEqual(resp.context["object_list"], [self.task2])

        resp = self.client.get(base, {"done": "0"})
        self.assertCountEqual(resp.context["object_list"], [self.task1, self.task3])

        resp = self.client.get(base, {"priority": "low"})
        self.assertCountEqual(resp.context["object_list"], [self.task3])

    def test_task_detail_requires_login(self):
        url = reverse("tracker:task-detail", args=[self.task1.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

    def test_task_create_sets_creator(self):
        self.client.login(username="u1", password="pass12345")
        url = reverse("tracker:task-create")
        data = {
            "name": "New Task",
            "description": "",
            "deadline": "",
            "priority": "medium",
            "task_type": self.task_type.id,
            "assignees": [self.other.id],
            "is_completed": False,
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        created = Task.objects.get(name="New Task")
        self.assertEqual(created.creator, self.user)
        self.assertIn(self.other, created.assignees.all())

    def test_task_update_requires_login(self):
        url = reverse("tracker:task-update", args=[self.task1.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

        self.client.login(username="u1", password="pass12345")
        resp = self.client.post(url, {
            "name": "T1-upd",
            "description": "",
            "deadline": "",
            "priority": "high",
            "task_type": self.task_type.id,
            "assignees": [self.user.id],
            "is_completed": True,
        })
        self.assertEqual(resp.status_code, 302)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.name, "T1-upd")
        self.assertTrue(self.task1.is_completed)
        self.assertEqual(self.task1.priority, "high")

    def test_task_toggle_complete(self):
        self.client.login(username="u1", password="pass12345")
        url = reverse("tracker:task-toggle", args=[self.task1.pk])
        resp = self.client.post(url, HTTP_REFERER=reverse("tracker:task-list"))
        self.assertEqual(resp.status_code, 302)
        self.task1.refresh_from_db()
        self.assertTrue(self.task1.is_completed)