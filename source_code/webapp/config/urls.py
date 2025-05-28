from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("agents/", include("agent.urls")),
    path("", include("main.urls")),
    path("api/", include("api.urls")),
    path("user/", include("user.urls")),
]
