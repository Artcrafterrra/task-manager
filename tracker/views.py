from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from tracker.models import Task, TaskType, Project, Team
from tracker.forms import TaskForm, TaskTypeForm, SignUpForm

User = get_user_model()


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 20
    template_name = "tracker/task_list.html"

    def get_queryset(self):
        qs = (
            Task.objects.select_related("task_type", "creator")
            .prefetch_related("assignees")
            .order_by("-created_at")
        )
        if self.request.GET.get("my"):
            qs = qs.filter(assignees=self.request.user)
        if self.request.GET.get("created"):
            qs = qs.filter(creator=self.request.user)
        if self.request.GET.get("done") == "1":
            qs = qs.filter(is_completed=True)
        if self.request.GET.get("done") == "0":
            qs = qs.filter(is_completed=False)
        if pr := self.request.GET.get("priority"):
            qs = qs.filter(priority=pr)
        return qs


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
                Project.objects.filter(team__members=self.request.user).distinct(),
                pk=project_pk,
            )
            initial["project"] = project
        return initial

    def form_valid(self, form):
        form.instance.creator = self.request.user
        project = form.cleaned_data.get("project")
        # Перевірка наявності проекту
        if project is None:
            form.add_error("project", "Please select a project.")
            return self.form_invalid(form)
        # Перевірка доступу до обраного проекту
        if not Project.objects.filter(pk=project.pk, team__members=self.request.user).exists():
            form.add_error("project", "You don't have access to this project.")
            return self.form_invalid(form)
        # Якщо у Task є поле team — встановити його автоматично з проекту
        if hasattr(form.instance, "team") and form.instance.team_id is None:
            form.instance.team = project.team
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tracker:task-list")


def task_toggle_complete(request, pk: int):
    task = get_object_or_404(Task, pk=pk)
    task.is_completed = not task.is_completed
    task.save(update_fields=["is_completed"])
    return redirect(request.META.get("HTTP_REFERER", reverse_lazy("tracker:task-list")))


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    template_name = "tracker/tasktype_list.html"
    context_object_name = "types"
    paginate_by = 20
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
    def get_queryset(self):
        return Project.objects.filter(team__members=self.request.user).order_by("name").distinct()

class MyTeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    template_name = "tracker/team_list.html"
    context_object_name = "teams"
    def get_queryset(self):
        return Team.objects.filter(members=self.request.user).order_by("name")

class TeamProjectListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Project
    template_name = "tracker/project_list.html"
    context_object_name = "projects"

    def test_func(self):
        team = get_object_or_404(Team, pk=self.kwargs["pk"])
        return team.members.filter(pk=self.request.user.pk).exists()

    def handle_no_permission(self):
        # Поведінка за замовчуванням: або редірект на логін, або 403 якщо залогінений
        return super().handle_no_permission()

    def get_queryset(self):
        return (
            Project.objects.filter(team_id=self.kwargs["pk"])
            .order_by("name")
            .distinct()
        )

class TeamTaskListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Task
    template_name = "tracker/task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def test_func(self):
        team = get_object_or_404(Team, pk=self.kwargs["pk"])
        return team.members.filter(pk=self.request.user.pk).exists()

    def handle_no_permission(self):
        return super().handle_no_permission()

    def get_queryset(self):
        return (
            Task.objects.select_related("task_type", "creator")
            .prefetch_related("assignees")
            .filter(project__team_id=self.kwargs["pk"])
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["team"] = get_object_or_404(Team, pk=self.kwargs["pk"])
        return ctx

class ProjectTaskListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Task
    template_name = "tracker/task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        return project.team.members.filter(pk=self.request.user.pk).exists()

    def handle_no_permission(self):
        return super().handle_no_permission()

    def get_queryset(self):
        return (
            Task.objects.select_related("task_type", "creator")
            .prefetch_related("assignees")
            .filter(project_id=self.kwargs["pk"])
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["project"] = get_object_or_404(Project, pk=self.kwargs["pk"])
        return ctx

class UserProfileView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = User
    template_name = "tracker/user_profile.html"
    context_object_name = "profile_user"

    def test_func(self):
        return self.request.user.is_staff or self.request.user.pk == int(self.kwargs["pk"])

    def handle_no_permission(self):
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile_user = self.object
        ctx["current_tasks"] = (
            Task.objects.filter(assignees=profile_user, is_completed=False)
            .select_related("task_type", "creator")
            .prefetch_related("assignees")
            .order_by("deadline", "-priority", "-created_at")
        )
        return ctx

def my_profile_redirect(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect("tracker:user-profile", pk=request.user.pk)