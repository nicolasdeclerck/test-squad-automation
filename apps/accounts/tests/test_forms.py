import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from apps.accounts.forms import LoginForm, ProfileForm, SignUpForm, UserForm

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


@pytest.mark.django_db
class TestLoginForm:
    def setup_method(self):
        self.factory = RequestFactory()
        self.password = "Str0ngP@ss!"
        self.user = UserFactory(email="test@example.com", password=self.password)

    def _get_form(self, data):
        request = self.factory.post("/comptes/connexion/")
        return LoginForm(request=request, data=data)

    def test_login_form_valid_credentials(self):
        form = self._get_form(
            {"username": "test@example.com", "password": self.password}
        )
        assert form.is_valid()

    def test_login_form_invalid_email(self):
        form = self._get_form(
            {"username": "nonexistent@example.com", "password": self.password}
        )
        assert not form.is_valid()

    def test_login_form_invalid_password(self):
        form = self._get_form(
            {"username": "test@example.com", "password": "wrongpassword"}
        )
        assert not form.is_valid()

    def test_login_form_email_label(self):
        request = self.factory.get("/comptes/connexion/")
        form = LoginForm(request=request)
        assert form.fields["username"].label == "Adresse email"

    def test_login_form_error_message_in_french(self):
        form = self._get_form(
            {"username": "test@example.com", "password": "wrongpassword"}
        )
        form.is_valid()
        errors = form.non_field_errors()
        assert any("incorrect" in str(e).lower() for e in errors)


@pytest.mark.django_db
class TestUserForm:
    def test_valid_data(self):
        form = UserForm(data={"first_name": "Jean", "last_name": "Dupont"})
        assert form.is_valid()

    def test_empty_fields_allowed(self):
        form = UserForm(data={"first_name": "", "last_name": ""})
        assert form.is_valid()

    def test_labels(self):
        form = UserForm()
        assert form.fields["first_name"].label == "Prénom"
        assert form.fields["last_name"].label == "Nom"


@pytest.mark.django_db
class TestProfileForm:
    def test_valid_avatar(self):
        from io import BytesIO

        from PIL import Image

        img = Image.new("RGB", (100, 100), "red")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        file = SimpleUploadedFile("avatar.jpg", buf.read(), content_type="image/jpeg")
        form = ProfileForm(data={}, files={"avatar": file})
        assert form.is_valid()

    def test_rejects_invalid_mime_type(self):
        file = SimpleUploadedFile(
            "test.txt", b"not an image", content_type="text/plain"
        )
        form = ProfileForm(data={}, files={"avatar": file})
        assert not form.is_valid()
        assert "avatar" in form.errors

    def test_rejects_oversized_file(self):
        data = b"x" * (5 * 1024 * 1024 + 1)
        file = SimpleUploadedFile("large.jpg", data, content_type="image/jpeg")
        form = ProfileForm(data={}, files={"avatar": file})
        assert not form.is_valid()
        assert "avatar" in form.errors
