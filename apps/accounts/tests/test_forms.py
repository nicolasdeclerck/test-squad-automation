import pytest
from django.contrib.auth import get_user_model

from apps.accounts.forms import SignUpForm

from .factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestSignUpForm:
    def test_signup_form_valid_data(self):
        form = SignUpForm(
            data={
                "email": "nouveau@example.com",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            }
        )
        assert form.is_valid()

    def test_signup_form_missing_email(self):
        form = SignUpForm(
            data={
                "email": "",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors

    def test_signup_form_duplicate_email(self):
        UserFactory(email="existe@example.com")
        form = SignUpForm(
            data={
                "email": "existe@example.com",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors

    def test_signup_form_duplicate_email_case_insensitive(self):
        UserFactory(email="Test@Example.com")
        form = SignUpForm(
            data={
                "email": "test@example.com",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors

    def test_signup_form_password_mismatch(self):
        form = SignUpForm(
            data={
                "email": "user@example.com",
                "password1": "Str0ngP@ss!",
                "password2": "DifferentPass!",
            }
        )
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_signup_form_password_too_short(self):
        form = SignUpForm(
            data={
                "email": "user@example.com",
                "password1": "short",
                "password2": "short",
            }
        )
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_signup_form_generates_username_from_email(self):
        form = SignUpForm(
            data={
                "email": "jean.dupont@example.com",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            }
        )
        assert form.is_valid()
        user = form.save()
        assert user.username.startswith("jean.dupont")
