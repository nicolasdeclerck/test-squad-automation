import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


class TestComingSoonView:
    def test_coming_soon_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_coming_soon_uses_correct_template(self, client):
        response = client.get("/")
        assert "core/coming_soon.html" in [t.name for t in response.templates]

    def test_coming_soon_contains_title(self, client):
        response = client.get("/")
        assert "Coming Soon" in response.content.decode()

    def test_coming_soon_has_meta_description(self, client):
        response = client.get("/")
        content = response.content.decode()
        assert '<meta name="description"' in content

    def test_coming_soon_has_seo_title(self, client):
        response = client.get("/")
        content = response.content.decode()
        assert "<title>" in content
        assert "Coming Soon" in content
