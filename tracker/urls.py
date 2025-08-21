from django.urls import path
from tracker.views import (
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskUpdateView,
    task_toggle_complete
)

app_name = "tracker"

urlpatterns = [
    path("", TaskListView.as_view(), name="task-list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/toggle/", task_toggle_complete, name="task-toggle"),
]