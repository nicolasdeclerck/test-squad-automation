import random

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Profile

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte avec cet email existe déjà.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        local_part = user.email.split("@")[0]
        username = local_part
        while User.objects.filter(username=username).exists():
            username = f"{local_part}_{random.randint(1000, 9999)}"
        user.username = username
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Adresse email"

    def clean(self):
        # Ne pas appeler super().clean() car AuthenticationForm.clean()
        # fait sa propre authentification qu'on remplace ici
        cleaned_data = super(AuthenticationForm, self).clean()
        email = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if email and password:
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "Adresse email ou mot de passe incorrect."
                )

            self.user_cache = authenticate(
                self.request, username=user.username, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Adresse email ou mot de passe incorrect."
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Adresse email",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            User.objects.filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Un compte avec cet email existe déjà.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar",)
        labels = {
            "avatar": "Avatar",
        }

    def save(self, commit=True):
        if not self.files.get("avatar") and self.instance.avatar:
            self.instance.avatar._committed = True
        return super().save(commit=commit)
