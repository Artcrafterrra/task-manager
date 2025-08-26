from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from tracker.models import Position, TaskType, Task, Team, Project
from .forms import AvatarUploadForm
from .models import Worker


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Company info", {"fields": ("position",)}),
        ("Profile", {"fields": ("avatar",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("avatar",)}),
    )
    list_display = ("username", "email", "position", "is_staff", "is_active")
    list_filter = ("position", "is_staff", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")

    inlines = []
    readonly_fields = ("projects_list",)

    def projects_list(self, obj):
        projects = (
            Project.objects.filter(team__members=obj)
            .order_by("name")
            .distinct()
        )
        return ", ".join(p.name for p in projects) or "—"

    projects_list.short_description = "Projects"


class TeamMembershipInline(admin.TabularInline):
    model = Team.members.through
    extra = 0
    verbose_name = "Team membership"
    verbose_name_plural = "Teams"


WorkerAdmin.inlines = [TeamMembershipInline]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    filter_horizontal = ("members",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "team")
    search_fields = ["name"]
    autocomplete_fields = ("team",)

