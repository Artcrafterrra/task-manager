from django.test import SimpleTestCase
from django.urls import reverse, resolve

from tracker.views import (
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskUpdateView,
    task_toggle_complete,
    TaskTypeListView,
    TaskTypeCreateView,
)


class TestUrls(SimpleTestCase):
    def test_task_urls(self):
        self.assertEqual(
            resolve(reverse("tracker:task-list")).func.view_class,
            TaskListView,
        )
        self.assertEqual(
            resolve(reverse("tracker:task-create")).func.view_class,
            TaskCreateView,
        )
        self.assertEqual(
            resolve(reverse("tracker:task-detail", args=[1])).func.view_class,
            TaskDetailView,
        )
        self.assertEqual(
            resolve(reverse("tracker:task-update", args=[1])).func.view_class,
            TaskUpdateView,
        )
        self.assertEqual(
            resolve(reverse("tracker:task-toggle", args=[1])).func,
            task_toggle_complete,
        )

    def test_tasktype_urls(self):
        self.assertEqual(
            resolve(reverse("tracker:tasktype-list")).func.view_class,
            TaskTypeListView,
        )
        self.assertEqual(
            resolve(reverse("tracker:tasktype-create")).func.view_class,
            TaskTypeCreateView,
        )
