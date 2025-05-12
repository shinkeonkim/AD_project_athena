from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.problem_view_set import ProblemViewSet

router = DefaultRouter()
router.register(r"", ProblemViewSet, basename="problem")

urlpatterns = [
    path("", include(router.urls)),
]
