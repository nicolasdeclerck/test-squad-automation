from unittest.mock import MagicMock, patch

import pytest
import requests as requests_lib
from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from apps.accounts.tests.factories import UserFactory
from apps.core.views import text_color_for_bg


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


@pytest.mark.django_db
class TestResponsiveMenu:
    def test_hamburger_button_present(self, client: Client):
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert 'id="menu-toggle"' in content

    def test_mobile_menu_present_and_hidden(self, client: Client):
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert 'id="mobile-menu"' in content
        assert 'id="mobile-menu" class="hidden md:hidden' in content

    def test_mobile_menu_nav_links(self, client: Client):
        response = client.get(reverse("home"))
        content = response.content.decode()
        mobile_menu = content.split('id="mobile-menu"')[1].split("</header>")[0]
        assert "Articles" in mobile_menu
        assert "À propos" in mobile_menu
        assert "Contact" in mobile_menu

    def test_mobile_menu_auth_buttons_anonymous(self, client: Client):
        response = client.get(reverse("home"))
        content = response.content.decode()
        mobile_menu = content.split('id="mobile-menu"')[1].split("</header>")[0]
        assert "Se connecter" in mobile_menu
        assert "Créer un compte" in mobile_menu

    def test_mobile_menu_auth_buttons_authenticated(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("home"))
        content = response.content.decode()
        mobile_menu = content.split('id="mobile-menu"')[1].split("</header>")[0]
        assert "Mon profil" in mobile_menu
        assert "Ajouter un article" in mobile_menu
        assert "Se déconnecter" in mobile_menu

    def test_desktop_nav_has_hidden_md_flex(self, client: Client):
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert 'class="hidden md:flex items-center gap-6"' in content
        assert 'class="hidden md:flex items-center gap-3"' in content


@pytest.mark.django_db
class TestAvatarDropdown:
    def test_navbar_shows_avatar_for_authenticated_user(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert 'id="avatar-dropdown-toggle"' in content

    def test_navbar_shows_initials_when_no_avatar(self, client: Client):
        user = UserFactory(username="alice")
        client.force_login(user)
        response = client.get(reverse("home"))
        content = response.content.decode()
        dropdown = content.split('id="avatar-dropdown-toggle"')[1].split("</button>")[0]
        assert "A" in dropdown

    def test_dropdown_contains_profile_link(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("home"))
        content = response.content.decode()
        dropdown_menu = content.split('id="avatar-dropdown-menu"')[1].split("</div>")[0]
        assert reverse("accounts:profile_edit") in dropdown_menu
        assert "Mon profil" in dropdown_menu

    def test_dropdown_contains_logout_form(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("home"))
        content = response.content.decode()
        dropdown_menu = content.split('id="avatar-dropdown-menu"')[1].split("</div>")[0]
        assert 'method="post"' in dropdown_menu
        assert reverse("accounts:logout") in dropdown_menu
        assert "Se déconnecter" in dropdown_menu

    def test_add_article_button_outside_dropdown(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("home"))
        content = response.content.decode()
        desktop_section = content.split('class="hidden md:flex items-center gap-3"')[1].split("</div>")[0]
        assert "Ajouter un article" in desktop_section
        dropdown_menu = content.split('id="avatar-dropdown-menu"')[1].split("</div>")[0]
        assert "Ajouter un article" not in dropdown_menu

    def test_navbar_desktop_no_auth_unchanged(self, client: Client):
        response = client.get(reverse("home"))
        content = response.content.decode()
        desktop_section = content.split('class="hidden md:flex items-center gap-3"')[1].split("</header>")[0]
        assert "Se connecter" in desktop_section
        assert "Créer un compte" in desktop_section
        assert 'id="avatar-dropdown-toggle"' not in desktop_section


def _mock_github_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or []
    return mock


MOCK_ISSUES = [
    {
        "title": "Bug: fix login",
        "labels": [
            {"name": "bug", "color": "d73a4a"},
            {"name": "priority", "color": "0075ca"},
        ],
    },
    {
        "title": "Feature: add search",
        "labels": [],
    },
]


@pytest.mark.django_db
class TestDevTrackingView:
    def setup_method(self):
        cache.clear()

    def test_dev_tracking_requires_login(self, client: Client):
        response = client.get(reverse("dev_tracking"))
        assert response.status_code == 302
        assert "/comptes/connexion/" in response.url

    @patch("apps.core.views.requests.get")
    def test_dev_tracking_authenticated_access(self, mock_get, client: Client):
        mock_get.return_value = _mock_github_response(200, MOCK_ISSUES)
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("dev_tracking"))
        assert response.status_code == 200
        assert "core/dev_tracking.html" in [
            t.name for t in response.templates
        ]

    @patch("apps.core.views.requests.get")
    def test_dev_tracking_displays_issues(self, mock_get, client: Client):
        mock_get.return_value = _mock_github_response(200, MOCK_ISSUES)
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("dev_tracking"))
        content = response.content.decode()
        assert "Bug: fix login" in content
        assert "Feature: add search" in content
        assert "bug" in content
        assert "priority" in content

    @patch("apps.core.views.requests.get")
    def test_dev_tracking_api_error_handling(self, mock_get, client: Client):
        mock_get.side_effect = requests_lib.ConnectionError("Connection error")
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("dev_tracking"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Impossible de" in content

    @patch("apps.core.views.requests.get")
    def test_dev_tracking_api_non_200(self, mock_get, client: Client):
        mock_get.return_value = _mock_github_response(500)
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("dev_tracking"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Impossible de" in content

    @patch("apps.core.views.requests.get")
    def test_dev_tracking_empty_issues(self, mock_get, client: Client):
        mock_get.return_value = _mock_github_response(200, [])
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("dev_tracking"))
        content = response.content.decode()
        assert "Aucune issue ouverte" in content

    @patch("apps.core.views.requests.get")
    def test_dev_tracking_uses_cache(self, mock_get, client: Client):
        mock_get.return_value = _mock_github_response(200, MOCK_ISSUES)
        user = UserFactory()
        client.force_login(user)
        client.get(reverse("dev_tracking"))
        client.get(reverse("dev_tracking"))
        assert mock_get.call_count == 1

    @patch("apps.core.views.requests.get")
    def test_dev_tracking_uses_settings_url(self, mock_get, client: Client, settings):
        settings.GITHUB_REPO_API_URL = "https://api.github.com/repos/test/repo"
        mock_get.return_value = _mock_github_response(200, [])
        user = UserFactory()
        client.force_login(user)
        client.get(reverse("dev_tracking"))
        called_url = mock_get.call_args[0][0]
        assert "test/repo" in called_url


class TestTextColorForBg:
    def test_light_background_returns_dark_text(self):
        assert text_color_for_bg("ffffff") == "#1f2937"

    def test_dark_background_returns_white_text(self):
        assert text_color_for_bg("000000") == "#ffffff"

    def test_yellow_returns_dark_text(self):
        assert text_color_for_bg("ffff00") == "#1f2937"

    def test_dark_red_returns_white_text(self):
        assert text_color_for_bg("d73a4a") == "#ffffff"


@pytest.mark.django_db
class TestFooterDevTrackingLink:
    def test_footer_link_visible_authenticated(self, client: Client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert "Suivi des devs" in content
        assert "/suivi-des-devs/" in content

    def test_footer_link_hidden_anonymous(self, client: Client):
        response = client.get(reverse("home"))
        content = response.content.decode()
        assert "Suivi des devs" not in content
