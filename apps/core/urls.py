from django.urls import path

from .views import AboutView, ContactView

urlpatterns = [
    path("a-propos/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
]
