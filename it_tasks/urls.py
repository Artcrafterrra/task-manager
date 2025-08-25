from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views
from django.conf.urls.static import static
from django.conf import settings

from tracker.views import SignUpView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tracker.urls", namespace="tracker")),
    path("accounts/login/", views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", views.LogoutView.as_view(), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("accounts/", include("allauth.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
