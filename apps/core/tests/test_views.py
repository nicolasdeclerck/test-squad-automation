import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestAboutView:
    def test_about_page_returns_200(self, client: Client):
        response = client.get(reverse("about"))
        assert response.status_code == 200

    def test_about_page_uses_correct_template(self, client: Client):
        response = client.get(reverse("about"))
        assert "core/about.html" in [
            t.name for t in response.templates
        ]

    def test_about_page_contains_nickorp(self, client: Client):
        response = client.get(reverse("about"))
        content = response.content.decode()
        assert "NICKORP" in content

    def test_about_page_has_title(self, client: Client):
        response = client.get(reverse("about"))
        content = response.content.decode()
        assert "<title>" in content
        assert "À propos" in content

    def test_about_page_has_meta_description(self, client: Client):
        response = client.get(reverse("about"))
        content = response.content.decode()
        assert "Découvrez NICKORP" in content

    def test_about_url_is_a_propos(self, client: Client):
        url = reverse("about")
        assert url == "/a-propos/"
