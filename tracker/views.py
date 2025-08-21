from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from tracker.models import Task
from tracker.forms import TaskForm


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

    def form_valid(self, form):
        form.instance.creator = self.request.user
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
