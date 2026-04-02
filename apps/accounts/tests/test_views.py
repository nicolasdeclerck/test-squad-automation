import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client

from .factories import UserFactory

User = get_user_model()

SIGNUP_URL = "/comptes/inscription/"
LOGIN_URL = "/comptes/connexion/"
LOGOUT_URL = "/comptes/deconnexion/"
PROFILE_EDIT_URL = "/comptes/profil/modifier/"


@pytest.mark.django_db
class TestSignUpView:
    def setup_method(self):
        self.client = Client()

    def test_signup_page_returns_200(self):
        response = self.client.get(SIGNUP_URL)
        assert response.status_code == 200

    def test_signup_page_uses_correct_template(self):
        response = self.client.get(SIGNUP_URL)
        assert "accounts/signup.html" in [t.name for t in response.templates]

    def test_signup_page_contains_form(self):
        response = self.client.get(SIGNUP_URL)
        content = response.content.decode()
        assert 'type="email"' in content
        assert 'type="password"' in content

    def test_signup_page_contains_csrf(self):
        response = self.client.get(SIGNUP_URL)
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content

    def test_signup_success_creates_user(self):
        self.client.post(
            SIGNUP_URL,
            {
                "email": "nouveau@example.com",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            },
        )
        assert User.objects.filter(email="nouveau@example.com").exists()

    def test_signup_success_redirects(self):
        response = self.client.post(
            SIGNUP_URL,
            {
                "email": "nouveau@example.com",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            },
        )
        assert response.status_code == 302

    def test_signup_success_logs_in_user(self):
        response = self.client.post(
            SIGNUP_URL,
            {
                "email": "nouveau@example.com",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            },
            follow=True,
        )
        assert response.wsgi_request.user.is_authenticated

    def test_signup_invalid_data_returns_200(self):
        response = self.client.post(
            SIGNUP_URL,
            {
                "email": "",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            },
        )
        assert response.status_code == 200

    def test_signup_invalid_data_shows_errors(self):
        response = self.client.post(
            SIGNUP_URL,
            {
                "email": "",
                "password1": "Str0ngP@ss!",
                "password2": "Str0ngP@ss!",
            },
        )
        content = response.content.decode()
        assert "errorlist" in content or "error" in content.lower()

    def test_signup_seo_title(self):
        response = self.client.get(SIGNUP_URL)
        content = response.content.decode()
        assert "<title>Créer un compte</title>" in content

    def test_signup_seo_meta_description(self):
        response = self.client.get(SIGNUP_URL)
        content = response.content.decode()
        assert "Créez votre compte pour accéder au blog." in content

    def test_signup_page_contains_login_link(self):
        response = self.client.get(SIGNUP_URL)
        content = response.content.decode()
        assert "/comptes/connexion/" in content


@pytest.mark.django_db
class TestLoginView:
    def setup_method(self):
        self.client = Client()
        self.password = "Str0ngP@ss!"
        self.user = UserFactory(email="login@example.com", password=self.password)

    def test_login_page_returns_200(self):
        response = self.client.get(LOGIN_URL)
        assert response.status_code == 200

    def test_login_page_uses_correct_template(self):
        response = self.client.get(LOGIN_URL)
        assert "accounts/login.html" in [t.name for t in response.templates]

    def test_login_page_contains_form(self):
        response = self.client.get(LOGIN_URL)
        content = response.content.decode()
        assert 'type="email"' in content
        assert 'type="password"' in content

    def test_login_page_contains_csrf(self):
        response = self.client.get(LOGIN_URL)
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content

    def test_login_success_redirects(self):
        response = self.client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": self.password},
        )
        assert response.status_code == 302

    def test_login_success_authenticates_user(self):
        response = self.client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": self.password},
            follow=True,
        )
        assert response.wsgi_request.user.is_authenticated
        assert response.wsgi_request.user == self.user

    def test_login_invalid_credentials_returns_200(self):
        response = self.client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": "wrongpass"},
        )
        assert response.status_code == 200

    def test_login_invalid_credentials_shows_error(self):
        response = self.client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": "wrongpass"},
        )
        content = response.content.decode()
        assert "incorrect" in content.lower() or "erreur" in content.lower()

    def test_login_seo_title(self):
        response = self.client.get(LOGIN_URL)
        content = response.content.decode()
        assert "<title>Se connecter</title>" in content

    def test_login_seo_meta_description(self):
        response = self.client.get(LOGIN_URL)
        content = response.content.decode()
        assert "Connectez-vous à votre compte pour accéder au blog." in content

    def test_login_contains_signup_link(self):
        response = self.client.get(LOGIN_URL)
        content = response.content.decode()
        assert "/comptes/inscription/" in content

    def test_login_redirects_authenticated_user(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(LOGIN_URL)
        assert response.status_code == 302

    def test_login_redirects_authenticated_user_to_home(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(LOGIN_URL)
        assert response.status_code == 302
        assert response.url == "/"

    def test_login_with_email(self):
        response = self.client.post(
            LOGIN_URL,
            {"username": "login@example.com", "password": self.password},
            follow=True,
        )
        assert response.wsgi_request.user.is_authenticated
        assert response.wsgi_request.user.email == "login@example.com"


@pytest.mark.django_db
class TestLogoutView:
    def setup_method(self):
        self.client = Client()
        self.password = "Str0ngP@ss!"
        self.user = UserFactory(email="logout@example.com", password=self.password)

    def test_logout_redirects_to_home(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(LOGOUT_URL)
        assert response.status_code == 302
        assert response.url == "/"

    def test_logout_actually_logs_out(self):
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(LOGOUT_URL)
        response = self.client.get("/")
        assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
class TestHomePageAuthButtons:
    def setup_method(self):
        self.client = Client()
        self.password = "Str0ngP@ss!"
        self.user = UserFactory(email="coming@example.com", password=self.password)

    def test_home_contains_login_link(self):
        response = self.client.get("/")
        content = response.content.decode()
        assert "/comptes/connexion/" in content

    def test_home_shows_login_link_for_anonymous(self):
        response = self.client.get("/")
        content = response.content.decode()
        assert "/comptes/connexion/" in content

    def test_home_shows_signup_link_for_anonymous(self):
        response = self.client.get("/")
        content = response.content.decode()
        assert "/comptes/inscription/" in content

    def test_home_hides_login_link_for_authenticated(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get("/")
        content = response.content.decode()
        assert "/comptes/connexion/" not in content

    def test_home_hides_signup_link_for_authenticated(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get("/")
        content = response.content.decode()
        assert "/comptes/inscription/" not in content

    def test_home_shows_logout_for_authenticated(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get("/")
        content = response.content.decode()
        assert "/comptes/deconnexion/" in content
        assert "csrfmiddlewaretoken" in content
        assert "Se déconnecter" in content


@pytest.mark.django_db
class TestProfileUpdateView:
    def setup_method(self):
        self.client = Client()
        self.password = "Str0ngP@ss!"
        self.user = UserFactory(email="profil@example.com", password=self.password)

    def test_redirects_anonymous_to_login(self):
        response = self.client.get(PROFILE_EDIT_URL)
        assert response.status_code == 302
        assert "/comptes/connexion/" in response.url

    def test_returns_200_for_authenticated(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(PROFILE_EDIT_URL)
        assert response.status_code == 200

    def test_uses_correct_template(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(PROFILE_EDIT_URL)
        assert "accounts/profile_edit.html" in [t.name for t in response.templates]

    def test_update_first_name_and_last_name(self):
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(
            PROFILE_EDIT_URL,
            {"first_name": "Jean", "last_name": "Dupont"},
        )
        self.user.refresh_from_db()
        assert self.user.first_name == "Jean"
        assert self.user.last_name == "Dupont"

    def test_upload_valid_avatar(self):
        from io import BytesIO

        from PIL import Image

        self.client.login(username=self.user.username, password=self.password)
        img = Image.new("RGB", (100, 100), "red")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        avatar = SimpleUploadedFile(
            "avatar.jpg", buf.read(), content_type="image/jpeg"
        )
        response = self.client.post(
            PROFILE_EDIT_URL,
            {"first_name": "", "last_name": "", "avatar": avatar},
        )
        assert response.status_code == 302
        self.user.profile.refresh_from_db()
        assert self.user.profile.avatar

    def test_upload_oversized_avatar_fails(self):
        self.client.login(username=self.user.username, password=self.password)
        data = b"x" * (5 * 1024 * 1024 + 1)
        avatar = SimpleUploadedFile("big.jpg", data, content_type="image/jpeg")
        response = self.client.post(
            PROFILE_EDIT_URL,
            {"first_name": "", "last_name": "", "avatar": avatar},
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "5 Mo" in content or "errorlist" in content

    def test_upload_invalid_file_type_fails(self):
        self.client.login(username=self.user.username, password=self.password)
        file = SimpleUploadedFile("doc.txt", b"hello", content_type="text/plain")
        response = self.client.post(
            PROFILE_EDIT_URL,
            {"first_name": "", "last_name": "", "avatar": file},
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "errorlist" in content or "error" in content.lower()

    def test_seo_title(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(PROFILE_EDIT_URL)
        content = response.content.decode()
        assert "<title>Modifier mon profil</title>" in content

    def test_seo_meta_description(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(PROFILE_EDIT_URL)
        content = response.content.decode()
        assert "Modifiez votre profil" in content

    def test_profile_link_visible_for_authenticated(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get("/")
        content = response.content.decode()
        assert "/comptes/profil/modifier/" in content

    def test_profile_link_hidden_for_anonymous(self):
        response = self.client.get("/")
        content = response.content.decode()
        assert "/comptes/profil/modifier/" not in content
