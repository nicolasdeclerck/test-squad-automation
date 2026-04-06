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

    def test_home_displays_author_name_when_available(self):
        post = PostFactory(
            author__first_name="Marie",
            author__last_name="Curie",
        )
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "Marie Curie" in content

    def test_home_displays_author_email_fallback_when_no_name(self):
        post = PostFactory(
            author__email="sans-nom@example.com",
            author__first_name="",
            author__last_name="",
        )
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "sans-nom@example.com" in content

    def test_home_displays_avatar_fallback_initial(self):
        import re

        post = PostFactory(author__email="bob@example.com")
        response = self.client.get(HOME_URL)
        content = response.content.decode()
        assert "bg-gray-300" in content
        match = re.search(r"bg-gray-300[^>]*>\s*([A-Z])\s*<", content)
        assert match is not None
        assert match.group(1) == "B"

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
        post = Post.objects.get(draft_title="Nouvel article")
        assert post.status == Post.STATUS_DRAFT
        assert post.has_draft is True

    def test_create_post_assigns_author(self):
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(
            CREATE_URL,
            {"title": "Mon article", "content": "Contenu"},
        )
        post = Post.objects.get(draft_title="Mon article")
        assert post.author == self.user

    def test_create_post_redirects_to_edit(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            CREATE_URL,
            {"title": "Article", "content": "Contenu"},
        )
        post = Post.objects.get(draft_title="Article")
        assert response.status_code == 302
        assert response.url == f"/articles/{post.slug}/modifier/"

    def test_create_post_empty_creates_draft(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            CREATE_URL,
            {"title": "", "content": ""},
        )
        assert response.status_code == 302
        assert Post.objects.filter(author=self.user, status=Post.STATUS_DRAFT).exists()

    def test_create_post_generates_slug(self):
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(
            CREATE_URL,
            {"title": "Mon super article", "content": "Contenu"},
        )
        post = Post.objects.get(draft_title="Mon super article")
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
        original_title = self.post.title
        original_content = self.post.content
        response = self.client.post(
            self.url,
            {"title": "Titre modifié", "content": "Contenu modifié"},
        )
        assert response.status_code == 302
        assert response.url == f"/articles/{self.post.slug}/modifier/"
        self.post.refresh_from_db()
        assert self.post.draft_title == "Titre modifié"
        assert self.post.draft_content == "Contenu modifié"
        assert self.post.has_draft is True
        assert self.post.title == original_title
        assert self.post.content == original_content

    def test_update_form_is_prefilled(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert self.post.title in content

    def test_update_form_prefills_draft_when_has_draft(self):
        self.post.draft_title = "Brouillon titre"
        self.post.draft_content = "Brouillon contenu"
        self.post.has_draft = True
        self.post.save()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        assert response.context["form"].initial["title"] == "Brouillon titre"
        assert response.context["form"].initial["content"] == "Brouillon contenu"

    def test_update_slug_does_not_change(self):
        original_slug = self.post.slug
        self.client.login(username=self.user.username, password=self.password)
        self.client.post(
            self.url,
            {"title": "Un tout nouveau titre", "content": "Contenu"},
        )
        self.post.refresh_from_db()
        assert self.post.slug == original_slug

    def test_update_empty_data_saves_successfully(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            self.url,
            {"title": "", "content": ""},
        )
        assert response.status_code == 302

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

    def test_list_displays_author_name_when_available(self):
        PostFactory(
            author__first_name="Albert",
            author__last_name="Einstein",
        )
        response = self.client.get(LIST_URL)
        content = response.content.decode()
        assert "Albert Einstein" in content

    def test_list_displays_author_email_fallback_when_no_name(self):
        PostFactory(
            author__email="anonyme@example.com",
            author__first_name="",
            author__last_name="",
        )
        response = self.client.get(LIST_URL)
        content = response.content.decode()
        assert "anonyme@example.com" in content

    def test_list_displays_avatar_fallback_initial(self):
        import re

        PostFactory(author__email="charlie@example.com")
        response = self.client.get(LIST_URL)
        content = response.content.decode()
        match = re.search(r"bg-gray-300[^>]*>\s*([A-Z])\s*<", content)
        assert match is not None
        assert match.group(1) == "C"

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

    def test_detail_returns_404_for_draft_anonymous(self):
        draft = PostFactory(status=Post.STATUS_DRAFT)
        response = self.client.get(f"/articles/{draft.slug}/")
        assert response.status_code == 404

    def test_detail_returns_200_for_draft_author(self):
        user = UserFactory(password=self.password)
        draft = PostFactory(
            status=Post.STATUS_DRAFT,
            author=user,
            draft_title="Mon brouillon",
        )
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(f"/articles/{draft.slug}/")
        assert response.status_code == 200

    def test_detail_returns_404_for_draft_other_user(self):
        other = UserFactory(password=self.password)
        draft = PostFactory(status=Post.STATUS_DRAFT)
        self.client.login(username=other.username, password=self.password)
        response = self.client.get(f"/articles/{draft.slug}/")
        assert response.status_code == 404

    def test_detail_returns_404_for_nonexistent_slug(self):
        response = self.client.get("/articles/slug-inexistant/")
        assert response.status_code == 404

    def test_detail_displays_post_author_name(self):
        user_with_name = UserFactory(
            first_name="Ada", last_name="Lovelace"
        )
        post = PostFactory(author=user_with_name)
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert "Ada Lovelace" in content

    def test_detail_displays_post_author_email_fallback(self):
        user_no_name = UserFactory(
            email="noname@example.com", first_name="", last_name=""
        )
        post = PostFactory(author=user_no_name)
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        assert "noname@example.com" in content

    def test_detail_displays_post_author_avatar_fallback(self):
        import re

        user = UserFactory(email="zoe@example.com")
        post = PostFactory(author=user)
        response = self.client.get(f"/articles/{post.slug}/")
        content = response.content.decode()
        # Find the article author section (before comments section)
        article_section = content.split('id="comments-section"')[0]
        match = re.search(
            r"bg-gray-300[^>]*>\s*([A-Z])\s*<", article_section
        )
        assert match is not None
        assert match.group(1) == "Z"

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

    def test_comments_not_scrollable(self):
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "max-h-96" not in content
        assert "overflow-y-auto" not in content

    def test_comment_displays_author_name_when_available(self):
        user_with_name = UserFactory(
            first_name="Jean", last_name="Dupont", password=self.password
        )
        CommentFactory(
            post=self.post,
            author=user_with_name,
            is_approved=True,
        )
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Jean Dupont" in content

    def test_comment_displays_email_when_no_name(self):
        user_no_name = UserFactory(
            first_name="", last_name="", password=self.password
        )
        CommentFactory(
            post=self.post,
            author=user_no_name,
            is_approved=True,
        )
        response = self.client.get(self.url)
        content = response.content.decode()
        assert user_no_name.email in content

    def test_comment_avatar_displayed(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        user_with_avatar = UserFactory(password=self.password)
        user_with_avatar.profile.avatar = SimpleUploadedFile(
            "avatar.jpg", b"\xff\xd8\xff\xe0", content_type="image/jpeg"
        )
        user_with_avatar.profile.save()
        CommentFactory(
            post=self.post,
            author=user_with_avatar,
            is_approved=True,
        )
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "<img" in content
        assert "rounded-full" in content

    def test_comment_avatar_fallback_initial(self):
        import re

        user_no_avatar = UserFactory(
            email="alice@example.com", password=self.password
        )
        CommentFactory(
            post=self.post,
            author=user_no_avatar,
            is_approved=True,
        )
        response = self.client.get(self.url)
        content = response.content.decode()
        # Search only in the comments section
        comments_section = content.split('id="comments-section"')[1]
        assert "bg-gray-300" in comments_section
        match = re.search(
            r"bg-gray-300[^>]*>\s*([A-Z])\s*<", comments_section
        )
        assert match is not None
        assert match.group(1) == "A"

    def test_delete_button_visible_for_author(self):
        user = UserFactory(password=self.password)
        comment = CommentFactory(
            post=self.post,
            author=user,
            is_approved=True,
        )
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert f"/commentaire/{comment.pk}/supprimer/" in content

    def test_delete_button_hidden_for_other_user(self):
        author = UserFactory(password=self.password)
        other = UserFactory(password=self.password)
        comment = CommentFactory(
            post=self.post,
            author=author,
            is_approved=True,
        )
        self.client.login(username=other.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert f"/commentaire/{comment.pk}/supprimer/" not in content

    def test_pagination_data_comment_attributes(self):
        for _ in range(12):
            CommentFactory(post=self.post, is_approved=True)
        response = self.client.get(self.url)
        content = response.content.decode()
        # Each comment div has data-comment attribute; JS also references it
        assert content.count("data-comment>") == 12
        assert "load-more-comments" in content

    def test_post_detail_comment_form_in_section(self):
        user = UserFactory(password=self.password)
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        comments_section = content.split('id="comments-section"')[1]
        assert "Publier le commentaire" in comments_section

    def test_post_detail_login_prompt_in_section(self):
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


@pytest.mark.django_db
class TestCommentDeleteView:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)
        self.post = PostFactory()
        self.comment = CommentFactory(
            post=self.post, author=self.user, is_approved=True
        )
        self.url = (
            f"/articles/{self.post.slug}"
            f"/commentaire/{self.comment.pk}/supprimer/"
        )

    def test_comment_delete_by_author(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(self.url)
        assert response.status_code == 302
        assert not Comment.objects.filter(pk=self.comment.pk).exists()

    def test_comment_delete_by_other_user(self):
        other = UserFactory(password=self.password)
        self.client.login(username=other.username, password=self.password)
        response = self.client.post(self.url)
        assert response.status_code == 404
        assert Comment.objects.filter(pk=self.comment.pk).exists()

    def test_comment_delete_anonymous(self):
        response = self.client.post(self.url)
        assert response.status_code == 302
        assert LOGIN_URL in response.url
        assert Comment.objects.filter(pk=self.comment.pk).exists()

    def test_comment_delete_get_not_allowed(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        assert response.status_code == 405
        assert Comment.objects.filter(pk=self.comment.pk).exists()


MY_POSTS_URL = "/mes-articles/"


@pytest.mark.django_db
class TestMyPostsListView:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)

    def test_my_posts_requires_auth(self):
        response = self.client.get(MY_POSTS_URL)
        assert response.status_code == 302
        assert LOGIN_URL in response.url

    def test_my_posts_returns_200(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(MY_POSTS_URL)
        assert response.status_code == 200

    def test_my_posts_shows_all_user_posts(self):
        PostFactory(author=self.user, status=Post.STATUS_PUBLISHED)
        PostFactory(
            author=self.user,
            status=Post.STATUS_DRAFT,
            draft_title="Brouillon",
        )
        PostFactory()  # another user's post
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(MY_POSTS_URL)
        assert len(response.context["posts"]) == 2

    def test_my_posts_does_not_show_others_posts(self):
        PostFactory()  # another user's post
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(MY_POSTS_URL)
        assert len(response.context["posts"]) == 0

    def test_my_posts_shows_draft_badge(self):
        PostFactory(
            author=self.user,
            status=Post.STATUS_DRAFT,
            draft_title="Mon brouillon",
        )
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(MY_POSTS_URL)
        content = response.content.decode()
        assert "Brouillon" in content

    def test_my_posts_shows_published_badge(self):
        PostFactory(author=self.user, status=Post.STATUS_PUBLISHED)
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(MY_POSTS_URL)
        content = response.content.decode()
        assert "Publié" in content

    def test_my_posts_paginates_by_10(self):
        PostFactory.create_batch(15, author=self.user)
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(MY_POSTS_URL)
        assert len(response.context["posts"]) == 10


@pytest.mark.django_db
class TestPostDetailVersionNavigation:
    def setup_method(self):
        self.client = Client()
        self.password = "testpass123"
        self.user = UserFactory(password=self.password)
        self.post = PostFactory(
            author=self.user,
            title="Version publiée",
            content="Contenu publié",
            status=Post.STATUS_PUBLISHED,
            has_draft=True,
            draft_title="Version brouillon",
            draft_content="Contenu brouillon",
        )
        self.url = f"/articles/{self.post.slug}/"

    def test_default_shows_published_version(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        assert response.context["display_title"] == "Version publiée"
        assert response.context["viewing_version"] == "published"

    def test_draft_param_shows_draft_version(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url + "?version=draft")
        assert response.context["display_title"] == "Version brouillon"
        assert response.context["viewing_version"] == "draft"

    def test_version_banner_visible_for_author(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "Versions" in content
        assert "?version=draft" in content

    def test_version_banner_hidden_for_non_author(self):
        other = UserFactory(password=self.password)
        self.client.login(username=other.username, password=self.password)
        response = self.client.get(self.url)
        content = response.content.decode()
        assert "?version=draft" not in content

    def test_draft_param_ignored_for_non_author(self):
        other = UserFactory(password=self.password)
        self.client.login(username=other.username, password=self.password)
        response = self.client.get(self.url + "?version=draft")
        assert response.context["display_title"] == "Version publiée"

    def test_draft_banner_for_unpublished_article(self):
        draft = PostFactory(
            author=self.user,
            status=Post.STATUS_DRAFT,
            draft_title="Mon brouillon",
        )
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(f"/articles/{draft.slug}/")
        content = response.content.decode()
        assert "Cet article est un brouillon" in content


@pytest.mark.django_db
class TestDraftVisibility:
    def setup_method(self):
        self.client = Client()

    def test_draft_not_in_home(self):
        PostFactory(status=Post.STATUS_DRAFT, draft_title="Brouillon secret")
        response = self.client.get(HOME_URL)
        assert "Brouillon secret" not in response.content.decode()

    def test_draft_not_in_public_list(self):
        PostFactory(status=Post.STATUS_DRAFT, draft_title="Brouillon secret")
        response = self.client.get(LIST_URL)
        assert "Brouillon secret" not in response.content.decode()

    def test_published_still_visible_in_home(self):
        PostFactory(title="Article publié", status=Post.STATUS_PUBLISHED)
        response = self.client.get(HOME_URL)
        assert "Article publié" in response.content.decode()

    def test_published_still_visible_in_list(self):
        PostFactory(title="Article publié", status=Post.STATUS_PUBLISHED)
        response = self.client.get(LIST_URL)
        assert "Article publié" in response.content.decode()
