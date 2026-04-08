from django.urls import path

from .api_views import (
    AvatarDeleteAPIView,
    CSRFTokenAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    ProfileUpdateAPIView,
    SignupAPIView,
)

urlpatterns = [
    path("csrf/", CSRFTokenAPIView.as_view(), name="api_csrf"),
    path("login/", LoginAPIView.as_view(), name="api_login"),
    path("signup/", SignupAPIView.as_view(), name="api_signup"),
    path("logout/", LogoutAPIView.as_view(), name="api_logout"),
    path("me/", MeAPIView.as_view(), name="api_me"),
    path("profile/", ProfileUpdateAPIView.as_view(), name="api_profile"),
    path(
        "avatar/delete/",
        AvatarDeleteAPIView.as_view(),
        name="api_avatar_delete",
    ),
]
