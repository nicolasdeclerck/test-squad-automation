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
class TestProfileUpdateEmailAPI:
    def setup_method(self):
        self.client = Client()

    def test_update_email(self):
        from django.test.client import MULTIPART_CONTENT, encode_multipart

        user = UserFactory(email="old@example.com")
        self.client.force_login(user)
        response = self.client.put(
            "/api/accounts/profile/",
            data=encode_multipart(
                "BoUnDaRyStRiNg",
                {"first_name": "Jean", "last_name": "Dupont", "email": "new@example.com"},
            ),
            content_type=MULTIPART_CONTENT,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "new@example.com"

    def test_update_email_duplicate(self):
        from django.test.client import MULTIPART_CONTENT, encode_multipart

        UserFactory(email="taken@example.com")
        user = UserFactory(email="mine@example.com")
        self.client.force_login(user)
        response = self.client.put(
            "/api/accounts/profile/",
            data=encode_multipart(
                "BoUnDaRyStRiNg",
                {"first_name": "Jean", "last_name": "Dupont", "email": "taken@example.com"},
            ),
            content_type=MULTIPART_CONTENT,
        )
        assert response.status_code == 400
        data = response.json()
        assert "email" in data

    def test_update_email_invalid_format(self):
        from django.test.client import MULTIPART_CONTENT, encode_multipart

        user = UserFactory(email="valid@example.com")
        self.client.force_login(user)
        response = self.client.put(
            "/api/accounts/profile/",
            data=encode_multipart(
                "BoUnDaRyStRiNg",
                {"first_name": "Jean", "last_name": "Dupont", "email": "invalid-email"},
            ),
            content_type=MULTIPART_CONTENT,
        )
        assert response.status_code == 400
        data = response.json()
        assert "email" in data

    def test_update_keeps_same_email(self):
        from django.test.client import MULTIPART_CONTENT, encode_multipart

        user = UserFactory(email="same@example.com")
        self.client.force_login(user)
        response = self.client.put(
            "/api/accounts/profile/",
            data=encode_multipart(
                "BoUnDaRyStRiNg",
                {"first_name": "Jean", "last_name": "Dupont", "email": "same@example.com"},
            ),
            content_type=MULTIPART_CONTENT,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "same@example.com"


@pytest.mark.django_db
class TestProfileUpdateAvatarValidationAPI:
    def setup_method(self):
        self.client = Client()

    def test_rejects_txt_file_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test.client import MULTIPART_CONTENT, encode_multipart

        user = UserFactory()
        self.client.force_login(user)
        txt_file = SimpleUploadedFile(
            "test.txt", b"hello world", content_type="text/plain"
        )
        response = self.client.put(
            "/api/accounts/profile/",
            data=encode_multipart(
                "BoUnDaRyStRiNg",
                {"first_name": "Jean", "last_name": "Dupont", "avatar": txt_file},
            ),
            content_type=MULTIPART_CONTENT,
        )
        assert response.status_code == 400
        data = response.json()
        assert "avatar" in data

    def test_rejects_fake_content_type_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test.client import MULTIPART_CONTENT, encode_multipart

        user = UserFactory()
        self.client.force_login(user)
        fake_file = SimpleUploadedFile(
            "fake.jpg", b"this is not an image", content_type="image/jpeg"
        )
        response = self.client.put(
            "/api/accounts/profile/",
            data=encode_multipart(
                "BoUnDaRyStRiNg",
                {"first_name": "Jean", "last_name": "Dupont", "avatar": fake_file},
            ),
            content_type=MULTIPART_CONTENT,
        )
        assert response.status_code == 400
        data = response.json()
        assert "avatar" in data

    def test_accepts_valid_jpeg_upload(self):
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test.client import MULTIPART_CONTENT, encode_multipart
        from PIL import Image

        user = UserFactory()
        self.client.force_login(user)
        # Créer une vraie image JPEG minimale
        buf = BytesIO()
        img = Image.new("RGB", (10, 10), color="red")
        img.save(buf, format="JPEG")
        buf.seek(0)
        jpeg_file = SimpleUploadedFile(
            "avatar.jpg", buf.read(), content_type="image/jpeg"
        )
        response = self.client.put(
            "/api/accounts/profile/",
            data=encode_multipart(
                "BoUnDaRyStRiNg",
                {"first_name": "Jean", "last_name": "Dupont", "avatar": jpeg_file},
            ),
            content_type=MULTIPART_CONTENT,
        )
        assert response.status_code == 200


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
