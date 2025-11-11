from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from tracker.models import Position, TaskType, Task, Team, Project
from .forms import AvatarUploadForm
from .models import Worker

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


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

    def save_model(self, request, obj, form, change):
        def compress_image(f):
            img = Image.open(f)
            img.load()
            max_size = (64, 64)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            has_alpha = img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            )

            buffer = BytesIO()
            if has_alpha:
                img = img.convert("RGBA")
                img.save(buffer, format="PNG", optimize=True)
                file_ext = "png"
                content_type = "image/png"
            else:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(
                    buffer,
                    format="JPEG",
                    quality=75,
                    optimize=True,
                    progressive=True,
                )
                file_ext = "jpg"
                content_type = "image/jpeg"

            buffer.seek(0)
            return InMemoryUploadedFile(
                buffer,
                field_name="ImageField",
                name=f"avatar_compressed.{file_ext}",
                content_type=content_type,
                size=buffer.getbuffer().nbytes,
                charset=None,
            )

        avatar = form.cleaned_data.get("avatar")
        if avatar:
            try:
                obj.avatar = compress_image(avatar)
            except Exception:
                pass
        super().save_model(request, obj, form, change)


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
