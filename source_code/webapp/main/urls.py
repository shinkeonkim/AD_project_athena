from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("test-500/", views.test_500_error, name="test_500_error"),
    path("test-403/", views.test_403_error, name="test_403_error"),
]
