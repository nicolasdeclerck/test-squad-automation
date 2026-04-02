from django.urls import path

from .views import LoginView, LogoutView, ProfileUpdateView, SignUpView

app_name = "accounts"

urlpatterns = [
    path("inscription/", SignUpView.as_view(), name="signup"),
    path("connexion/", LoginView.as_view(), name="login"),
    path("deconnexion/", LogoutView.as_view(), name="logout"),
    path("profil/modifier/", ProfileUpdateView.as_view(), name="profile_edit"),
]
