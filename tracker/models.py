from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy
from cloudinary_storage.storage import MediaCloudinaryStorage


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="workers",
        null=True,
        blank=True,
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        storage=MediaCloudinaryStorage(),
        null=True,
        blank=True,
        help_text="Image for profile",
    )

    class Meta:
        ordering = ["username"]

    def __str__(self):
        full = self.get_full_name()
        return full or self.username

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            from .models import Team

            team_name = getattr(settings, "DEFAULT_TEAM_NAME", "Team One")
            team, _ = Team.objects.get_or_create(name=team_name)
            team.members.add(self)


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=80, unique=True)
    members = models.ManyToManyField(
        "Worker", related_name="teams", blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=120, unique=True)
    team = models.ForeignKey(
        Team, on_delete=models.PROTECT, related_name="projects"
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    class Priority(models.TextChoices):
        URGENT = "urgent", gettext_lazy("Urgent")
        HIGH = "high", gettext_lazy("High")
        MEDIUM = "medium", gettext_lazy("Medium")
        LOW = "low", gettext_lazy("Low")

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False, db_index=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
    )

    task_type = models.ForeignKey(
        TaskType, on_delete=models.PROTECT, related_name="tasks"
    )
    creator = models.ForeignKey(
        "Worker", on_delete=models.CASCADE, related_name="created_tasks"
    )
    assignees = models.ManyToManyField(
        "Worker", related_name="assigned_tasks", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField("Tag", related_name="tasks", blank=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_completed", "deadline"]),
            models.Index(fields=["priority", "deadline"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="deadline_not_before_created",
                check=models.Q(deadline__isnull=True)
                | models.Q(deadline__gte=models.F("created_at")),
            ),
        ]

    def __str__(self):
        return self.name
