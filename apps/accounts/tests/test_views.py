import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

SIGNUP_URL = "/comptes/inscription/"


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
