from api.agent.views import QuestionTaskRatingViewSet, QuestionTaskViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"questions", QuestionTaskViewSet, basename="question-task")
router.register(
    r"question-ratings", QuestionTaskRatingViewSet, basename="question-task-rating"
)

urlpatterns = [
    path("", include(router.urls)),
]
