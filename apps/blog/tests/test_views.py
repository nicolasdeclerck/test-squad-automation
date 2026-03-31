import pytest
from django.test import Client

from apps.accounts.tests.factories import UserFactory
from apps.blog.models import Post

from .factories import PostFactory

HOME_URL = "/"
CREATE_URL = "/articles/creer/"
LIST_URL = "/articles/"
LOGIN_URL = "/comptes/connexion/"


@pytest.mark.django_db
class TestHomeView:
    def setup_method(self):
        self.client = Client()

    def test_home_returns_200(self):
        response = self.client.get(HOME_URL)
        assert response.status_code == 200

    def test_home_uses_correct_template(self):
        response = self.client.get(HOME_URL)
        assert "blog/home.html" in [t.name for t in response.templates]

    def test_home_displays_max_10_posts(self):
        PostFactory.create_batch(12)
        response = self.client.get(HOME_URL)
        assert len(response.context["posts"]) == 10

    def test_home_displays_author_email(self):
        post = PostFactory(author__email="auteur@example.com")
        response = self.client.get(HOME_URL)
        assert "auteur@example.com" in response.content.decode()

    def test_home_displays_date_dd_mm_yyyy(self):
        post = PostFactory()
        response = self.client.get(HOME_URL)
        expected_date = post.created_at.strftime("%d/%m/%Y")
        assert expected_date in response.content.decode()

    def test_home_shows_full_list_link_when_more_than_10(self):
        PostFactory.create_batch(11)
        response = self.client.get(HOME_URL)
        assert response.context["show_full_list_link"] is True
        assert "Voir tous les articles" in response.content.decode()

    def test_home_hides_full_list_link_when_10_or_less(self):
        PostFactory.create_batch(10)
        response = self.client.get(HOME_URL)
        assert response.context["show_full_list_link"] is False
        assert "Voir tous les articles" not in response.content.decode()

    def test_home_shows_add_button_for_authenticated(self):
        user = UserFactory()
        self.client.login(username=user.username, password="testpass123")
        response = self.client.get(HOME_URL)
        assert "Ajouter un article" in response.content.decode()

    def test_home_hides_add_button_for_anonymous(self):
        response = self.client.get(HOME_URL)
        assert "Ajouter un article" not in response.content.decode()

    def test_home_seo_title(self):
        response = self.client.get(HOME_URL)
        assert "<title>Blog</title>" in response.content.decode()

    def test_home_seo_meta_description(self):
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "Découvrez les derniers articles de notre blog." in content

    def test_home_shows_login_link_for_anonymous(self):
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "/comptes/connexion/" in content

    def test_home_shows_signup_link_for_anonymous(self):
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "/comptes/inscription/" in content

    def test_home_hides_login_link_for_authenticated(self):
        user = UserFactory()
        self.client.login(username=user.username, password="testpass123")
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "/comptes/connexion/" not in content

    def test_home_hides_signup_link_for_authenticated(self):
        user = UserFactory()
        self.client.login(username=user.username, password="testpass123")
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "/comptes/inscription/" not in content

    def test_home_shows_logout_for_authenticated(self):
        user = UserFactory()
        self.client.login(username=user.username, password="testpass123")
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "/comptes/deconnexion/" in content
        assert "Se déconnecter" in content


@pytest.mark.django_db
class TestPostCreateView:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)

    def test_create_returns_200_for_authenticated(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(CREATE_URL)
        assert response.status_code == 200

    def test_create_redirects_anonymous_to_login(self):
        response = self.client.get(CREATE_URL)
        assert response.status_code == 302
        assert LOGIN_URL in response.url

    def test_create_post_success(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            CREATE_URL,
            {"title": "Nouvel article", "content": "Contenu de l'article"},
        )
        assert Post.objects.filter(title="Nouvel article").exists()

    def test_create_post_assigns_author(self):
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(
            CREATE_URL,
            {"title": "Mon article", "content": "Contenu"},
        )
        post = Post.objects.get(title="Mon article")
        assert post.author == self.user

    def test_create_post_redirects_to_home(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            CREATE_URL,
            {"title": "Article", "content": "Contenu"},
        )
        assert response.status_code == 302
        assert response.url == "/"

    def test_create_post_invalid_returns_200(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            CREATE_URL,
            {"title": "", "content": ""},
        )
        assert response.status_code == 200

    def test_create_post_generates_slug(self):
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(
            CREATE_URL,
            {"title": "Mon super article", "content": "Contenu"},
        )
        post = Post.objects.get(title="Mon super article")
        assert post.slug == "mon-super-article"

    def test_create_seo_title(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(CREATE_URL)
        assert "<title>Ajouter un article</title>" in response.content.decode()

    def test_create_seo_meta_description(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(CREATE_URL)
        content = response.content.decode()
        assert "Créez un nouvel article sur le blog." in content


@pytest.mark.django_db
class TestPostListView:
    def setup_method(self):
        self.client = Client()

    def test_list_returns_200(self):
        response = self.client.get(LIST_URL)
        assert response.status_code == 200

    def test_list_paginates_by_10(self):
        PostFactory.create_batch(15)
        response = self.client.get(LIST_URL)
        assert len(response.context["posts"]) == 10

    def test_list_ordered_by_date_desc(self):
        posts = PostFactory.create_batch(3)
        response = self.client.get(LIST_URL)
        result_pks = [p.pk for p in response.context["posts"]]
        expected_pks = [
            p.pk
            for p in Post.objects.filter(status=Post.STATUS_PUBLISHED).order_by(
                "-created_at"
            )
        ]
        assert result_pks == expected_pks

    def test_list_seo_title(self):
        response = self.client.get(LIST_URL)
        assert "<title>Tous les articles</title>" in response.content.decode()

    def test_list_seo_meta_description(self):
        response = self.client.get(LIST_URL)
        content = response.content.decode()
        assert "Liste complète des articles du blog." in content
