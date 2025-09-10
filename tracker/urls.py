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
    MyTeamListView,
    TeamProjectListView,
    TeamTaskListView,
    ProjectTaskListView,
    UserProfileView,
    my_profile_redirect,
    user_avatar_upload,
    ProjectCreateView,
    TaskDeleteView,
)

app_name = "tracker"

urlpatterns = [
    path("", TaskListView.as_view(), name="task-list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path(
        "tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"
    ),
    path("tasks/<int:pk>/toggle/", task_toggle_complete, name="task-toggle"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("types/", TaskTypeListView.as_view(), name="tasktype-list"),
    path(
        "types/create/", TaskTypeCreateView.as_view(), name="tasktype-create"
    ),
    path("projects/", MyProjectListView.as_view(), name="project-list"),
    path(
        "projects/create/", ProjectCreateView.as_view(), name="project-create"
    ),
    path(
        "projects/<int:pk>/tasks/",
        ProjectTaskListView.as_view(),
        name="project-tasks",
    ),
    path(
        "projects/<int:project_pk>/tasks/create/",
        TaskCreateView.as_view(),
        name="task-create-in-project",
    ),
    path("teams/", MyTeamListView.as_view(), name="team-list"),
    path(
        "teams/<int:pk>/projects/",
        TeamProjectListView.as_view(),
        name="team-projects",
    ),
    path(
        "teams/<int:pk>/tasks/", TeamTaskListView.as_view(), name="team-tasks"
    ),
    path("users/<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path(
        "users/<int:pk>/avatar/",
        user_avatar_upload,
        name="user-avatar-upload",
    ),
    path("me/", my_profile_redirect, name="my-profile"),
]
