from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("problems/", include("api.problem.urls")),
    path("agents/", include("api.agent.urls")),
]
