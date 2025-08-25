from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from tracker.models import Task, Project, TaskType, Position

User = get_user_model()


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(
            is_active=True, is_superuser=False
        ),  # тільки активні, без суперюзерів
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


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(), required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "position",
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            from django.core.exceptions import ValidationError

            raise ValidationError("User with such email already exists.")
        return email
