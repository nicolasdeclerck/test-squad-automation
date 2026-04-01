from django.urls import path

from .views import AboutView

urlpatterns = [
    path("a-propos/", AboutView.as_view(), name="about"),
]
