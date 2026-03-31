import random

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

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
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

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
