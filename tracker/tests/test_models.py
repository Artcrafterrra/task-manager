import datetime
from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from tracker.models import Position, TaskType, Worker, Tag, Task

User = get_user_model()


class TestModels(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.task_type = TaskType.objects.create(name="Bug")
        self.creator = User.objects.create_user(
            username="creator",
            password="pass12345",
            first_name="John",
            last_name="Doe",
            position=self.position,
        )

    def test_str_methods(self):
        self.assertEqual(str(self.position), "Developer")
        self.assertEqual(str(self.task_type), "Bug")
        user = User.objects.create_user(username="jane", password="pass12345")
        self.assertEqual(str(user), "jane")  # без імені показує username
        tag = Tag.objects.create(name="backend")
        self.assertEqual(str(tag), "backend")
        task = Task.objects.create(
            name="Fix login",
            task_type=self.task_type,
            creator=self.creator,
        )
        self.assertEqual(str(task), "Fix login")

    def test_task_indexes_and_ordering(self):
        t1 = Task.objects.create(
            name="A", task_type=self.task_type, creator=self.creator
        )
        t2 = Task.objects.create(
            name="B", task_type=self.task_type, creator=self.creator
        )
        self.assertEqual(list(Task.objects.all()), [t2, t1])

    def test_task_deadline_check_constraint(self):
        past_date = timezone.now().date() - datetime.timedelta(days=365 * 5)
        with self.assertRaises(IntegrityError):
            Task.objects.create(
                name="Impossible deadline",
                task_type=self.task_type,
                creator=self.creator,
                deadline=past_date,
            )

    def test_task_priority_choices(self):
        task = Task.objects.create(
            name="Medium task",
            task_type=self.task_type,
            creator=self.creator,
        )
        self.assertEqual(task.priority, Task.Priority.MEDIUM)
        task.priority = Task.Priority.HIGH
        task.save(update_fields=["priority"])
        task.refresh_from_db()
        self.assertEqual(task.priority, Task.Priority.HIGH)
