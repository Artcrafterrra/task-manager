from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.db.models import Q, Prefetch

from tracker.models import Task, TaskType, Project, Team, Worker
from tracker.forms import TaskForm, TaskTypeForm, SignUpForm, AvatarUploadForm

User = get_user_model()


class TeamMemberRequiredMixin(UserPassesTestMixin):
    team_pk_kwarg = "pk"

    def get_team(self):
        return get_object_or_404(Team, pk=self.kwargs[self.team_pk_kwarg])

    def test_func(self):
        team = self.get_team()
        return team.members.filter(pk=self.request.user.pk).exists()

    def handle_no_permission(self):
        return super().handle_no_permission()


class ProjectMemberRequiredMixin(UserPassesTestMixin):
    project_pk_kwarg = "pk"

    def get_project(self):
        return get_object_or_404(
            Project, pk=self.kwargs[self.project_pk_kwarg]
        )

    def test_func(self):
        project = self.get_project()
        return project.team.members.filter(pk=self.request.user.pk).exists()

    def handle_no_permission(self):
        return super().handle_no_permission()


class TaskFiltersMixin:
    allowed_filters = set()

    def apply_task_filters(self, qs):
        if not getattr(self.request.user, "position_id", None):
            return qs.none()

        if "q" in self.allowed_filters:
            if q := self.request.GET.get("q"):
                qs = qs.filter(
                    Q(name__icontains=q) | Q(description__icontains=q)
                )

        if "priority" in self.allowed_filters:
            pr_raw = self.request.GET.get("priority")
            if pr_raw:
                pr = str(pr_raw).strip().lower()
                numeric_map = {
                    "1": Task.Priority.LOW,
                    "2": Task.Priority.MEDIUM,
                    "3": Task.Priority.HIGH,
                    "4": Task.Priority.URGENT,
                }
                word_map = {
                    "low": Task.Priority.LOW,
                    "medium": Task.Priority.MEDIUM,
                    "high": Task.Priority.HIGH,
                    "urgent": Task.Priority.URGENT,
                }
                val = numeric_map.get(pr) or word_map.get(pr)
                if val:
                    qs = qs.filter(priority=val)

        if "my" in self.allowed_filters and self.request.GET.get("my"):
            qs = qs.filter(assignees=self.request.user)

        if "created" in self.allowed_filters and self.request.GET.get(
            "created"
        ):
            qs = qs.filter(creator=self.request.user)

        if "done" in self.allowed_filters:
            done = self.request.GET.get("done")
            if done == "1":
                qs = qs.filter(is_completed=True)
            elif done == "0":
                qs = qs.filter(is_completed=False)

        return qs


class TaskListView(LoginRequiredMixin, TaskFiltersMixin, generic.ListView):
    model = Task
    paginate_by = 10
    template_name = "tracker/task_list.html"
    context_object_name = "tasks"
    allowed_filters = {"q", "priority", "my", "created", "done"}

    def get_queryset(self):
        qs = (
            Task.objects.select_related("task_type", "creator")
            .prefetch_related("assignees")
            .order_by("-created_at")
        )
        return self.apply_task_filters(qs).distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search_query"] = self.request.GET.get("q", "")
        return ctx


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    template_name = "tracker/task_detail.html"


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tracker:task-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        project_pk = self.kwargs.get("project_pk")
        if project_pk:
            project = get_object_or_404(
                Project.objects.filter(
                    team__members=self.request.user
                ).distinct(),
                pk=project_pk,
            )
            initial["project"] = project
        return initial

    def form_valid(self, form):
        form.instance.creator = self.request.user
        project = form.cleaned_data.get("project")
        if project is None:
            form.add_error("project", "Please select a project.")
            return self.form_invalid(form)
        if not Project.objects.filter(
            pk=project.pk, team__members=self.request.user
        ).exists():
            form.add_error(
                "project", "You don't have access to this project."
            )
            return self.form_invalid(form)
        if hasattr(form.instance, "team") and form.instance.team_id is None:
            form.instance.team = project.team
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tracker:task-list")


def task_toggle_complete(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    if (
        not task.project
        or not task.project.team.members.filter(pk=request.user.pk).exists()
    ):
        return redirect(
            request.META.get(
                "HTTP_REFERER", reverse_lazy("tracker:task-list")
            )
        )
    task.is_completed = not task.is_completed
    task.save(update_fields=["is_completed"])
    return redirect(
        request.META.get("HTTP_REFERER", reverse_lazy("tracker:task-list"))
    )


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    template_name = "tracker/tasktype_list.html"
    context_object_name = "types"
    paginate_by = 10
    ordering = ["name"]


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    form_class = TaskTypeForm
    template_name = "tracker/tasktype_form.html"
    success_url = reverse_lazy("tracker:tasktype-list")


class SignUpView(UserPassesTestMixin, generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("tracker:task-list")

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return super().handle_no_permission()

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_success_url(self):
        from django.conf import settings

        return getattr(settings, "LOGIN_REDIRECT_URL", str(self.success_url))

    def get_object(self, queryset=None):
        return None


class MyProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    template_name = "tracker/project_list.html"
    context_object_name = "projects"
    paginate_by = 10

    def get_queryset(self):
        return (
            Project.objects.filter(team__members=self.request.user)
            .order_by("name")
            .distinct()
        )


class MyTeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    template_name = "tracker/team_list.html"
    context_object_name = "teams"
    paginate_by = 10

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user).order_by("name")


class TeamProjectListView(
    LoginRequiredMixin, TeamMemberRequiredMixin, generic.ListView
):
    model = Project
    template_name = "tracker/project_list.html"
    context_object_name = "projects"
    paginate_by = 10

    def get_queryset(self):
        return (
            Project.objects.filter(team_id=self.kwargs["pk"])
            .order_by("name")
            .distinct()
        )


class TeamTaskListView(
    LoginRequiredMixin,
    TeamMemberRequiredMixin,
    TaskFiltersMixin,
    generic.ListView,
):
    model = Task
    template_name = "tracker/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10
    allowed_filters = {"q", "priority", "done"}

    def get_queryset(self):
        qs = (
            Task.objects.select_related(
                "task_type", "creator", "project", "project__team"
            )
            .prefetch_related("assignees")
            .filter(project__team_id=self.kwargs["pk"])
            .order_by("-created_at")
        )
        return self.apply_task_filters(qs).distinct()


class ProjectTaskListView(
    LoginRequiredMixin,
    ProjectMemberRequiredMixin,
    TaskFiltersMixin,
    generic.ListView,
):
    model = Task
    template_name = "tracker/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10
    allowed_filters = {"q", "priority", "done"}

    def get_queryset(self):
        qs = (
            Task.objects.select_related(
                "task_type", "creator", "project", "project__team"
            )
            .prefetch_related("assignees")
            .filter(project_id=self.kwargs["pk"])
            .order_by("-created_at")
        )
        return self.apply_task_filters(qs).distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["project"] = get_object_or_404(Project, pk=self.kwargs["pk"])
        return ctx


class UserProfileView(
    LoginRequiredMixin, UserPassesTestMixin, generic.DetailView
):
    model = User
    template_name = "tracker/user_profile.html"
    context_object_name = "profile_user"

    def test_func(self):
        return self.request.user.is_staff or self.request.user.pk == int(
            self.kwargs["pk"]
        )

    def handle_no_permission(self):
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile_user = self.object
        if getattr(profile_user, "position_id", None):
            ctx["current_tasks"] = (
                Task.objects.filter(
                    assignees=profile_user, is_completed=False
                )
                .select_related("task_type", "creator")
                .prefetch_related("assignees")
                .order_by("deadline", "-priority", "-created_at")
            )
        else:
            ctx["current_tasks"] = Task.objects.none()
        return ctx


def my_profile_redirect(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect("tracker:user-profile", pk=request.user.pk)


class BaseTaskListView(
    LoginRequiredMixin, TaskFiltersMixin, generic.ListView
):
    model = Task
    paginate_by = 10
    template_name = "tracker/task_list.html"

    def base_qs(self):
        return (
            Task.objects.select_related("task_type", "creator")
            .prefetch_related(
                Prefetch(
                    "assignees", queryset=User.objects.only("id", "username")
                )
            )
            .order_by("-created_at")
        )


@login_required
def user_avatar_upload(request, pk):
    profile_user = get_object_or_404(Worker, pk=pk)
    if request.user != profile_user and not request.user.is_staff:
        messages.error(request, "No permission to edit this profile.")
        return redirect(
            reverse("tracker:user-profile", args=[profile_user.pk])
        )

    if request.method == "POST":
        form = AvatarUploadForm(
            request.POST, request.FILES, instance=profile_user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Avatar updated.")
        else:
            for err in form.errors.get("avatar", []):
                messages.error(request, err)
        return redirect(
            reverse("tracker:user-profile", args=[profile_user.pk])
        )

    return redirect(reverse("tracker:user-profile", args=[profile_user.pk]))
