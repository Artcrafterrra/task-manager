from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Position, TaskType, Worker, Task


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
    fieldsets = UserAdmin.fieldsets + (("Company info", {"fields": ("position",)}),)
    list_display = ("username", "email", "position", "is_staff", "is_active")
    list_filter = ("position", "is_staff", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "task_type", "priority", "is_completed", "deadline", "creator")
    list_filter = ("task_type", "priority", "is_completed", "deadline")
    search_fields = ("name", "description")
    autocomplete_fields = ("task_type", "assignees", "creator")
    filter_horizontal = ("assignees",)
