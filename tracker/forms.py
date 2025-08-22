from django import forms
from django.contrib.auth import get_user_model

from tracker.models import Task, TaskType


User = get_user_model()


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True, is_superuser=False),  # тільки активні, без суперюзерів
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="assignees",
    )


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignees"].queryset = (
            User.objects.filter(is_superuser=False, is_active=True)
            .select_related("position")
            .order_by("first_name", "last_name", "username")
        )


class TaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if TaskType.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Such task type already exists.")
        return name