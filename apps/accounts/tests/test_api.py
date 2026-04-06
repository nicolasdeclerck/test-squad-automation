import json

import pytest
from django.test import Client

from .factories import UserFactory


@pytest.mark.django_db
class TestCSRFAPI:
    def test_csrf_returns_token(self):
        client = Client(enforce_csrf_checks=False)
        response = client.get("/api/accounts/csrf/")
        assert response.status_code == 200
        assert "csrfToken" in response.json()


@pytest.mark.django_db
class TestLoginAPI:
    def setup_method(self):
        self.client = Client()

    def test_login_success(self):
        user = UserFactory(email="test@example.com")
        response = self.client.post(
            "/api/accounts/login/",
            data=json.dumps({"email": "test@example.com", "password": "testpass123"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_login_wrong_password(self):
        UserFactory(email="test@example.com")
        response = self.client.post(
            "/api/accounts/login/",
            data=json.dumps({"email": "test@example.com", "password": "wrong"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_login_unknown_email(self):
        response = self.client.post(
            "/api/accounts/login/",
            data=json.dumps(
                {"email": "unknown@example.com", "password": "testpass123"}
            ),
            content_type="application/json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestSignupAPI:
    def setup_method(self):
        self.client = Client()

    def test_signup_success(self):
        response = self.client.post(
            "/api/accounts/signup/",
            data=json.dumps(
                {
                    "email": "new@example.com",
                    "password1": "StrongPass123!",
                    "password2": "StrongPass123!",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"

    def test_signup_password_mismatch(self):
        response = self.client.post(
            "/api/accounts/signup/",
            data=json.dumps(
                {
                    "email": "new@example.com",
                    "password1": "StrongPass123!",
                    "password2": "DifferentPass!",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_signup_duplicate_email(self):
        UserFactory(email="taken@example.com")
        response = self.client.post(
            "/api/accounts/signup/",
            data=json.dumps(
                {
                    "email": "taken@example.com",
                    "password1": "StrongPass123!",
                    "password2": "StrongPass123!",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogoutAPI:
    def test_logout_requires_auth(self):
        client = Client()
        response = client.post("/api/accounts/logout/")
        assert response.status_code == 403

    def test_logout_success(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        response = client.post("/api/accounts/logout/")
        assert response.status_code == 204


@pytest.mark.django_db
class TestMeAPI:
    def setup_method(self):
        self.client = Client()

    def test_me_authenticated(self):
        user = UserFactory(email="me@example.com")
        self.client.force_login(user)
        response = self.client.get("/api/accounts/me/")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"

    def test_me_unauthenticated(self):
        response = self.client.get("/api/accounts/me/")
        assert response.status_code == 200
        assert response.json()["id"] is None


@pytest.mark.django_db
class TestProfileUpdateAPI:
    def setup_method(self):
        self.client = Client()

    def test_update_profile_requires_auth(self):
        response = self.client.put("/api/accounts/profile/")
        assert response.status_code == 403

    def test_update_profile(self):
        from django.test.client import MULTIPART_CONTENT, encode_multipart

        user = UserFactory()
        self.client.force_login(user)
        response = self.client.put(
            "/api/accounts/profile/",
            data=encode_multipart(
                "BoUnDaRyStRiNg",
                {"first_name": "Jean", "last_name": "Dupont"},
            ),
            content_type=MULTIPART_CONTENT,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jean"
        assert data["last_name"] == "Dupont"


@pytest.mark.django_db
class TestAvatarDeleteAPI:
    def test_delete_avatar_requires_auth(self):
        client = Client()
        response = client.delete("/api/accounts/avatar/delete/")
        assert response.status_code == 403

    def test_delete_avatar(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        response = client.delete("/api/accounts/avatar/delete/")
        assert response.status_code == 204
