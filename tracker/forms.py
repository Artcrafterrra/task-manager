from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from tracker.models import Task, Project, TaskType, Position

User = get_user_model()


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(
            is_active=True, is_superuser=False
        ),
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
            "project",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Task name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Describe the task...",
                    "rows": 8,
                }
            ),
            "deadline": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "task_type": forms.Select(attrs={"class": "form-select"}),
            "project": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if "project" in self.fields:
            if self.user and getattr(self.user, "is_authenticated", False):
                self.fields["project"].queryset = (
                    Project.objects.filter(team__members=self.user)
                    .order_by("name")
                    .distinct()
                )
            self.fields["project"].label = "Project"


class TaskTypeForm(forms.ModelForm):
    class Meta:
        model = TaskType
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Type name",
                    "autofocus": "autofocus",
                }
            ),
        }
        labels = {
            "name": "Name",
        }
        help_texts = {
            "name": "Enter a short, clear name for the task type.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields have CoreUI/Bootstrap styles if added later
        for f in self.fields.values():
            css = f.widget.attrs.get("class", "")
            if "form-control" not in css and not isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs["class"] = (css + " form-control").strip()

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if TaskType.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Such task type already exists.")
        return name


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, required=False, label="First name"
    )
    last_name = forms.CharField(
        max_length=150, required=False, label="Last name"
    )
    email = forms.EmailField(required=False, label="Email")
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(), required=False, label="Position"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "User with such email already exists."
            )
        return email
