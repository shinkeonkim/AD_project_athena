from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("agents/", include("agent.urls")),
    path("", include("main.urls")),
    path("api/", include("api.urls")),
    path("user/", include("user.urls")),
]
