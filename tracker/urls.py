from django.urls import path
from tracker.views import (
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskUpdateView,
    task_toggle_complete,
    TaskTypeListView,
    TaskTypeCreateView,
    MyProjectListView,
    MyTeamListView
)

app_name = "tracker"

urlpatterns = [
    path("", TaskListView.as_view(), name="task-list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/toggle/", task_toggle_complete, name="task-toggle"),
    path("types/", TaskTypeListView.as_view(), name="tasktype-list"),
    path("types/create/", TaskTypeCreateView.as_view(), name="tasktype-create"),
    path("projects/", MyProjectListView.as_view(), name="project-list"),
    path("teams/", MyTeamListView.as_view(), name="team-list"),
]