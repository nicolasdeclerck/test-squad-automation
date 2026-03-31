from django.urls import path

from .views import SignUpView

app_name = "accounts"

urlpatterns = [
    path("inscription/", SignUpView.as_view(), name="signup"),
]
