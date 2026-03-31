import json

import pytest
from django.test import Client
from django.urls import reverse

from apps.blog.models import Post
from apps.blog.tests.factories import PostFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestPostListView:
    def test_status_code(self, client):
        response = client.get(reverse("blog:post_list"))
        assert response.status_code == 200

    def test_only_published_posts(self, client):
        PostFactory(status=Post.STATUS_PUBLISHED, title="Publié")
        PostFactory(status=Post.STATUS_DRAFT, title="Brouillon")
        response = client.get(reverse("blog:post_list"))
        assert b"Publi" in response.content
        assert b"Brouillon" not in response.content

    def test_template_used(self, client):
        response = client.get(reverse("blog:post_list"))
        assert "blog/post_list.html" in [
            t.name for t in response.templates
        ]


class TestPostDetailView:
    def test_status_code(self, client):
        post = PostFactory(status=Post.STATUS_PUBLISHED)
        response = client.get(
            reverse("blog:post_detail", kwargs={"slug": post.slug})
        )
        assert response.status_code == 200

    def test_template_used(self, client):
        post = PostFactory()
        response = client.get(
            reverse("blog:post_detail", kwargs={"slug": post.slug})
        )
        assert "blog/post_detail.html" in [
            t.name for t in response.templates
        ]

    def test_404_for_nonexistent_slug(self, client):
        response = client.get(
            reverse("blog:post_detail", kwargs={"slug": "does-not-exist"})
        )
        assert response.status_code == 404


class TestPostCreateView:
    def test_login_required(self, client):
        response = client.get(reverse("blog:post_create"))
        assert response.status_code == 302

    def test_authenticated_user_can_access(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("blog:post_create"))
        assert response.status_code == 200

    def test_contains_blocknote_editor_container(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("blog:post_create"))
        assert b'id="blocknote-editor"' in response.content

    def test_js_script_loaded(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("blog:post_create"))
        assert b"index.js" in response.content

    def test_initial_json_in_context(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("blog:post_create"))
        assert b"blocknote-initial-data" in response.content

    def test_create_post(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        blocks = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Nouveau contenu"}],
            }
        ]
        response = client.post(
            reverse("blog:post_create"),
            data={
                "title": "Nouvel article",
                "status": "draft",
                "content_json": json.dumps(blocks),
                "content": "<p>Nouveau contenu</p>",
            },
        )
        assert response.status_code == 302
        post = Post.objects.get(title="Nouvel article")
        assert post.author == user
        assert post.content_json == blocks


class TestPostUpdateView:
    def test_login_required(self, client):
        post = PostFactory()
        response = client.get(
            reverse("blog:post_update", kwargs={"slug": post.slug})
        )
        assert response.status_code == 302

    def test_author_can_edit(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        post = PostFactory(author=user)
        response = client.get(
            reverse("blog:post_update", kwargs={"slug": post.slug})
        )
        assert response.status_code == 200

    def test_non_author_forbidden(self):
        client = Client()
        other_user = UserFactory()
        client.force_login(other_user)
        post = PostFactory()
        response = client.get(
            reverse("blog:post_update", kwargs={"slug": post.slug})
        )
        assert response.status_code == 403

    def test_initial_json_passed_for_edit(self):
        client = Client()
        user = UserFactory()
        client.force_login(user)
        blocks = [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Existant"}],
            }
        ]
        post = PostFactory(author=user, content_json=blocks)
        response = client.get(
            reverse("blog:post_update", kwargs={"slug": post.slug})
        )
        assert b"Existant" in response.content
