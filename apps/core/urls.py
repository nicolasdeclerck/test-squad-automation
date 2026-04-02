from django.urls import path

from .views import AboutView, ContactView, DevTrackingView

urlpatterns = [
    path("a-propos/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("suivi-des-devs/", DevTrackingView.as_view(), name="dev_tracking"),
]
