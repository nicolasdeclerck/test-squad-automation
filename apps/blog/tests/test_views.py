import re

import pytest
from django.test import Client

from apps.accounts.tests.factories import UserFactory
from apps.blog.models import Comment, Post

from .factories import CommentFactory, PostFactory

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
        assert "<title>NICKORP</title>" in response.content.decode()

    def test_home_header_displays_nickorp(self):
        response = self.client.get(HOME_URL)
        assert "NICKORP</a>" in response.content.decode()

    def test_home_footer_displays_nickorp(self):
        response = self.client.get(HOME_URL)
        assert "NICKORP" in response.content.decode()
        assert "Blog" not in response.content.decode().split("<footer")[1]

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

    def test_post_form_textarea_visible_without_js(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(CREATE_URL)
        content = response.content.decode()
        assert 'id="id_content"' in content
        # The textarea must not have 'hidden' class in its server-rendered HTML
        textarea_match = re.search(r"<textarea[^>]*id=\"id_content\"[^>]*>", content)
        assert textarea_match is not None
        assert "hidden" not in textarea_match.group(0)


@pytest.mark.django_db
class TestPostUpdateView:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)
        self.post = PostFactory(author=self.user)
        self.url = f"/articles/{self.post.slug}/modifier/"

    def test_update_returns_200_for_author(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_update_redirects_anonymous_to_login(self):
        response = self.client.get(self.url)
        assert response.status_code == 302
        assert LOGIN_URL in response.url

    def test_update_returns_404_for_non_author(self):
        other_user = UserFactory(password=self.password)
        self.client.login(
            username=other_user.username, password=self.password
        )
        response = self.client.get(self.url)
        assert response.status_code == 404

    def test_update_post_success(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            self.url,
            {"title": "Titre modifié", "content": "Contenu modifié"},
        )
        assert response.status_code == 302
        assert response.url == "/"
        self.post.refresh_from_db()
        assert self.post.title == "Titre modifié"
        assert self.post.content == "Contenu modifié"

    def test_update_form_is_prefilled(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert self.post.title in content
        assert response.context["form"].initial["content"] == self.post.content

    def test_update_slug_does_not_change(self):
        original_slug = self.post.slug
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(
            self.url,
            {"title": "Un tout nouveau titre", "content": "Contenu"},
        )
        self.post.refresh_from_db()
        assert self.post.slug == original_slug

    def test_update_invalid_data_returns_200(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            self.url,
            {"title": "", "content": ""},
        )
        assert response.status_code == 200

    def test_update_seo_title(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "<title>Modifier l&#x27;article</title>" in content or "<title>Modifier l'article</title>" in content

    def test_update_seo_meta_description(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Modifiez votre article sur le blog." in content


@pytest.mark.django_db
class TestPostDeleteView:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)
        self.post = PostFactory(author=self.user)
        self.url = f"/articles/{self.post.slug}/supprimer/"

    def test_delete_returns_200_for_author(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_delete_redirects_anonymous_to_login(self):
        response = self.client.get(self.url)
        assert response.status_code == 302
        assert LOGIN_URL in response.url

    def test_delete_returns_404_for_non_author(self):
        other_user = UserFactory(password=self.password)
        self.client.login(
            username=other_user.username, password=self.password
        )
        response = self.client.get(self.url)
        assert response.status_code == 404

    def test_delete_post_success(self):
        self.client.login(username=self.user.username, password=self.password)
        post_pk = self.post.pk
        response = self.client.post(self.url)
        assert response.status_code == 302
        assert response.url == "/"
        assert not Post.objects.filter(pk=post_pk).exists()

    def test_delete_post_no_longer_in_db(self):
        self.client.login(username=self.user.username, password=self.password)
        post_pk = self.post.pk
        self.client.post(self.url)
        assert Post.objects.filter(pk=post_pk).count() == 0

    def test_delete_seo_title(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        assert "<title>Supprimer l&#x27;article</title>" in response.content.decode() or "<title>Supprimer l'article</title>" in response.content.decode()

    def test_delete_seo_meta_description(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Confirmez la suppression de votre article." in content


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


@pytest.mark.django_db
class TestPostDetailView:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.post = PostFactory(
            title="Article test",
            content="Contenu de test pour l'article",
        )
        self.url = f"/articles/{self.post.slug}/"

    def test_detail_returns_200_for_published(self):
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_detail_returns_404_for_draft(self):
        draft = PostFactory(status=Post.STATUS_DRAFT)
        response = self.client.get(f"/articles/{draft.slug}/")
        assert response.status_code == 404

    def test_detail_returns_404_for_nonexistent_slug(self):
        response = self.client.get("/articles/slug-inexistant/")
        assert response.status_code == 404

    def test_detail_displays_approved_comments(self):
        comment = CommentFactory(
            post=self.post, is_approved=True, content="Commentaire visible"
        )
        response = self.client.get(self.url)
        assert "Commentaire visible" in response.content.decode()

    def test_detail_hides_unapproved_comments(self):
        comment = CommentFactory(
            post=self.post, is_approved=False, content="Commentaire masqué"
        )
        response = self.client.get(self.url)
        assert "Commentaire masqué" not in response.content.decode()

    def test_detail_shows_comment_form_for_authenticated(self):
        user = UserFactory(password=self.password)
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(self.url)
        assert "comment_form" in response.context
        assert "Publier le commentaire" in response.content.decode()

    def test_detail_shows_login_link_for_anonymous(self):
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Connectez-vous" in content
        assert "comment_form" not in response.context

    def test_detail_seo_title(self):
        response = self.client.get(self.url)
        assert f"<title>{self.post.title}</title>" in response.content.decode()

    def test_detail_seo_meta_description(self):
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Contenu de test" in content

    def test_post_detail_shows_comment_count(self):
        CommentFactory(post=self.post, is_approved=True)
        CommentFactory(post=self.post, is_approved=True)
        CommentFactory(post=self.post, is_approved=False)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "2 commentaires" in content

    def test_post_detail_shows_comment_count_singular(self):
        CommentFactory(post=self.post, is_approved=True)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "1 commentaire" in content
        assert "1 commentaires" not in content

    def test_post_detail_comments_section_hidden_by_default(self):
        response = self.client.get(self.url)
        content = response.content.decode()
        assert 'id="comments-section" class="hidden' in content

    def test_post_detail_toggle_button_present(self):
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Voir les commentaires" in content
        assert 'id="toggle-comments"' in content

    def test_post_detail_comment_form_in_dropdown(self):
        user = UserFactory(password=self.password)
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        comments_section = content.split('id="comments-section"')[1]
        assert "Publier le commentaire" in comments_section

    def test_post_detail_login_prompt_in_dropdown(self):
        response = self.client.get(self.url)
        content = response.content.decode()
        comments_section = content.split('id="comments-section"')[1]
        assert "Connectez-vous" in comments_section


@pytest.mark.django_db
class TestCommentCreateView:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)
        self.post = PostFactory()
        self.url = f"/articles/{self.post.slug}/commenter/"

    def test_comment_redirects_anonymous_to_login(self):
        response = self.client.post(
            self.url, {"content": "Un commentaire"}
        )
        assert response.status_code == 302
        assert LOGIN_URL in response.url

    def test_comment_creates_with_is_approved_false(self):
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(self.url, {"content": "Mon commentaire"})
        comment = Comment.objects.get(content="Mon commentaire")
        assert comment.is_approved is False

    def test_comment_assigns_author(self):
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(self.url, {"content": "Mon commentaire"})
        comment = Comment.objects.get(content="Mon commentaire")
        assert comment.author == self.user

    def test_comment_redirects_to_detail(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            self.url, {"content": "Mon commentaire"}
        )
        assert response.status_code == 302
        assert response.url == f"/articles/{self.post.slug}/"

    def test_comment_empty_content_fails(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(self.url, {"content": ""})
        assert Comment.objects.count() == 0
