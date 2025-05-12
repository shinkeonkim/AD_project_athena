from api.agent.views import QuestionTaskViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"questions", QuestionTaskViewSet, basename="question")

urlpatterns = [
    path("", include(router.urls)),
]
