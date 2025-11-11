from django.contrib.auth import get_user_model
from .models import Task, Project, Team

User = get_user_model()


def sidebar(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user
    my_open_tasks = (
        Task.objects.filter(assignees=user, is_completed=False)
        .select_related("task_type")
        .order_by("-created_at")[:5]
    )

    teams = Team.objects.filter(members=user).order_by("name")
    projects = (
        Project.objects.filter(team__members=user).order_by("name").distinct()
    )

    return {
        "sb_user": user,
        "sb_my_open_tasks": my_open_tasks,
        "sb_teams": teams,
        "sb_projects": projects,
    }
