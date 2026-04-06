import json

import pytest
from django.test import Client

from apps.accounts.tests.factories import UserFactory

from .factories import CommentFactory, PostFactory

API_POSTS_URL = "/api/blog/posts/"


def api_post_url(slug):
    return f"/api/blog/posts/{slug}/"


def api_comments_url(slug):
    return f"/api/blog/posts/{slug}/comments/"


def api_comment_delete_url(pk):
    return f"/api/blog/comments/{pk}/"


@pytest.mark.django_db
class TestPostListAPI:
    def setup_method(self):
        self.client = Client()

    def test_list_returns_200(self):
        response = self.client.get(API_POSTS_URL)
        assert response.status_code == 200

    def test_list_returns_published_posts(self):
        PostFactory.create_batch(3)
        response = self.client.get(API_POSTS_URL)
        data = response.json()
        assert data["count"] == 3

    def test_list_excludes_drafts(self):
        PostFactory(status="draft")
        PostFactory(status="published")
        response = self.client.get(API_POSTS_URL)
        data = response.json()
        assert data["count"] == 1

    def test_list_pagination(self):
        PostFactory.create_batch(15)
        response = self.client.get(API_POSTS_URL)
        data = response.json()
        assert len(data["results"]) == 10
        assert data["count"] == 15

    def test_list_contains_author_info(self):
        PostFactory(author__first_name="Jean", author__last_name="Dupont")
        response = self.client.get(API_POSTS_URL)
        data = response.json()
        author = data["results"][0]["author"]
        assert author["first_name"] == "Jean"
        assert author["last_name"] == "Dupont"

    def test_list_contains_plain_content(self):
        PostFactory(content='[{"type":"paragraph","content":[{"type":"text","text":"Hello world"}]}]')
        response = self.client.get(API_POSTS_URL)
        data = response.json()
        assert "Hello world" in data["results"][0]["plain_content"]


@pytest.mark.django_db
class TestPostDetailAPI:
    def setup_method(self):
        self.client = Client()

    def test_detail_returns_200(self):
        post = PostFactory()
        response = self.client.get(api_post_url(post.slug))
        assert response.status_code == 200

    def test_detail_returns_content(self):
        post = PostFactory(content="Test content")
        response = self.client.get(api_post_url(post.slug))
        data = response.json()
        assert data["content"] == "Test content"
        assert data["title"] == post.title

    def test_detail_returns_approved_comments(self):
        post = PostFactory()
        CommentFactory(post=post, is_approved=True, content="Approved")
        CommentFactory(post=post, is_approved=False, content="Pending")
        response = self.client.get(api_post_url(post.slug))
        data = response.json()
        assert len(data["approved_comments"]) == 1
        assert data["approved_comments"][0]["content"] == "Approved"

    def test_detail_is_owner_true_for_author(self):
        user = UserFactory()
        post = PostFactory(author=user)
        self.client.force_login(user)
        response = self.client.get(api_post_url(post.slug))
        data = response.json()
        assert data["is_owner"] is True

    def test_detail_is_owner_false_for_other(self):
        post = PostFactory()
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.get(api_post_url(post.slug))
        data = response.json()
        assert data["is_owner"] is False

    def test_detail_draft_returns_404(self):
        post = PostFactory(status="draft")
        response = self.client.get(api_post_url(post.slug))
        assert response.status_code == 404


@pytest.mark.django_db
class TestPostCreateAPI:
    def setup_method(self):
        self.client = Client()

    def test_create_requires_auth(self):
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps({"title": "Test", "content": "Content"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_create_post(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps({"title": "New Post", "content": "Some content"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Post"
        assert data["slug"] == "new-post"

    def test_create_post_auto_slug_dedup(self):
        user = UserFactory()
        PostFactory(title="Same Title")
        self.client.force_login(user)
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps({"title": "Same Title", "content": "Content"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "same-title-1"


@pytest.mark.django_db
class TestPostUpdateAPI:
    def setup_method(self):
        self.client = Client()

    def test_update_own_post(self):
        user = UserFactory()
        post = PostFactory(author=user)
        self.client.force_login(user)
        response = self.client.patch(
            api_post_url(post.slug),
            data=json.dumps({"title": "Updated Title"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_update_other_user_post_forbidden(self):
        post = PostFactory()
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.patch(
            api_post_url(post.slug),
            data=json.dumps({"title": "Hacked"}),
            content_type="application/json",
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestPostDeleteAPI:
    def setup_method(self):
        self.client = Client()

    def test_delete_own_post(self):
        user = UserFactory()
        post = PostFactory(author=user)
        self.client.force_login(user)
        response = self.client.delete(api_post_url(post.slug))
        assert response.status_code == 204

    def test_delete_other_user_post_forbidden(self):
        post = PostFactory()
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.delete(api_post_url(post.slug))
        assert response.status_code == 403


@pytest.mark.django_db
class TestCommentCreateAPI:
    def setup_method(self):
        self.client = Client()

    def test_create_comment_requires_auth(self):
        post = PostFactory()
        response = self.client.post(
            api_comments_url(post.slug),
            data=json.dumps({"content": "Nice post!"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_create_comment(self):
        user = UserFactory()
        post = PostFactory()
        self.client.force_login(user)
        response = self.client.post(
            api_comments_url(post.slug),
            data=json.dumps({"content": "Great article!"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Great article!"
        assert data["is_approved"] is False


@pytest.mark.django_db
class TestCommentDeleteAPI:
    def setup_method(self):
        self.client = Client()

    def test_delete_own_comment(self):
        user = UserFactory()
        comment = CommentFactory(author=user)
        self.client.force_login(user)
        response = self.client.delete(api_comment_delete_url(comment.pk))
        assert response.status_code == 204

    def test_delete_other_user_comment_forbidden(self):
        comment = CommentFactory()
        other = UserFactory()
        self.client.force_login(other)
        response = self.client.delete(api_comment_delete_url(comment.pk))
        assert response.status_code == 404
