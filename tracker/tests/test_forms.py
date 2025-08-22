from django.test import TestCase
from django.contrib.auth import get_user_model

from tracker.forms import TaskForm, TaskTypeForm, SignUpForm
from tracker.models import Position, TaskType

User = get_user_model()


class TestTaskForm(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="QA")
        self.active_user = User.objects.create_user(
            username="active_user", password="pass12345", is_active=True, position=self.position
        )
        self.inactive_user = User.objects.create_user(
            username="inactive_user", password="pass12345", is_active=False, position=self.position
        )
        self.superuser = User.objects.create_superuser(
            username="admin", password="pass12345", email="admin@example.com"
        )
        self.task_type = TaskType.objects.create(name="Feature")

    def test_assignees_queryset_filters_and_ordering(self):
        form = TaskForm()
        qs = form.fields["assignees"].queryset
        self.assertIn(self.active_user, qs)
        self.assertNotIn(self.inactive_user, qs)
        self.assertNotIn(self.superuser, qs)
        for field in ["name", "description", "deadline", "priority", "task_type", "assignees", "is_completed"]:
            self.assertIn(field, form.fields)

    def test_valid_form_minimal(self):
        form = TaskForm(
            data={
                "name": "Task X",
                "description": "",
                "deadline": "",
                "priority": "medium",
                "task_type": self.task_type.id,
                "assignees": [self.active_user.id],
                "is_completed": False,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)


class TestTaskTypeForm(TestCase):
    def test_clean_name_unique_case_insensitive(self):
        TaskType.objects.create(name="Ops")
        form = TaskTypeForm(data={"name": "ops"})  # case-insensitive дубль
        self.assertFalse(form.is_valid())
        self.assertIn("Such task type already exists.", form.errors["name"])


class TestSignUpForm(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="PM")

    def test_signup_form_fields_and_email_uniqueness(self):
        user = User.objects.create_user(username="john", email="user@example.com", password="pass12345")
        form = SignUpForm(
            data={
                "username": "jane",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "USER@example.com",  # case-insensitive
                "password1": "aStrongPassword123",
                "password2": "aStrongPassword123",
                "position": self.position.id,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("User with such email already exists.", form.errors["email"])

    def test_signup_form_valid(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "first_name": "",
                "last_name": "",
                "email": "",
                "password1": "aStrongPassword123",
                "password2": "aStrongPassword123",
                "position": self.position.id,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.username, "newuser")