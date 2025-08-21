from django import forms
from tracker.models import Task, TaskType


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "deadline",
            "priority",
            "task_type",
            "assignees",
            "is_completed",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }


class TaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if TaskType.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Such task type already exists.")
        return name