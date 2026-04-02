from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from .forms import LoginForm, ProfileForm, SignUpForm, UserForm


class AvatarDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = ""
            profile.save()
            messages.success(request, "Votre avatar a été supprimé.")
        return redirect("accounts:profile_edit")


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class LogoutView(auth_views.LogoutView):
    pass


class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = "accounts/profile_edit.html"

    def get(self, request):
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return self._render(request, user_form, profile_form)

    def post(self, request):
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Votre profil a été mis à jour.")
            return redirect("accounts:profile_edit")
        return self._render(request, user_form, profile_form)

    def _render(self, request, user_form, profile_form):
        from django.template.response import TemplateResponse

        return TemplateResponse(
            request,
            self.template_name,
            {"user_form": user_form, "profile_form": profile_form},
        )
