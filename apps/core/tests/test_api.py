import pytest
from django.test import Client

from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestDevTrackingAPI:
    def setup_method(self):
        self.client = Client()

    def test_requires_authentication(self):
        response = self.client.get("/api/core/dev-tracking/")
        assert response.status_code == 403

    def test_returns_200_for_authenticated(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/api/core/dev-tracking/")
        assert response.status_code == 200

    def test_response_structure(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/api/core/dev-tracking/")
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert "page" in data
        assert "total_pages" in data
        assert "api_error" in data

    def test_pagination_param(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/api/core/dev-tracking/?page=2")
        data = response.json()
        assert data["page"] == 2
