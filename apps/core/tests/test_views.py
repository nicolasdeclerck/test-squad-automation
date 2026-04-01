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


@pytest.mark.django_db
class TestContactView:
    def test_contact_page_returns_200(self, client: Client):
        response = client.get(reverse("contact"))
        assert response.status_code == 200

    def test_contact_page_uses_correct_template(self, client: Client):
        response = client.get(reverse("contact"))
        assert "core/contact.html" in [t.name for t in response.templates]

    def test_contact_page_contains_nickorp(self, client: Client):
        response = client.get(reverse("contact"))
        content = response.content.decode()
        assert "NICKORP" in content

    def test_contact_page_has_title(self, client: Client):
        response = client.get(reverse("contact"))
        content = response.content.decode()
        assert "<title>" in content
        assert "Contact" in content

    def test_contact_page_has_meta_description(self, client: Client):
        response = client.get(reverse("contact"))
        content = response.content.decode()
        assert "Contactez NICKORP" in content

    def test_contact_url_is_contact(self, client: Client):
        url = reverse("contact")
        assert url == "/contact/"

    def test_contact_page_contains_github_link(self, client: Client):
        response = client.get(reverse("contact"))
        content = response.content.decode()
        assert "https://github.com/nicolasdeclerck/" in content

    def test_contact_page_contains_linkedin_link(self, client: Client):
        response = client.get(reverse("contact"))
        content = response.content.decode()
        assert "https://www.linkedin.com/in/nicolas-declerck/" in content

    def test_contact_link_in_navigation(self, client: Client):
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert "Contact" in content
        assert reverse("contact") in content
