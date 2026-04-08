from django.urls import path

from .api_views import DevTrackingAPIView

urlpatterns = [
    path(
        "dev-tracking/",
        DevTrackingAPIView.as_view(),
        name="api_dev_tracking",
    ),
]
