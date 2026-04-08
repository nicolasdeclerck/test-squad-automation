import json

import pytest
from django.test import Client

from apps.accounts.tests.factories import SuperUserFactory, UserFactory
from apps.blog.models import Post

from .factories import PostFactory, PostVersionFactory
from .helpers import (
    API_POSTS_URL,
    api_autosave_url,
    api_post_url,
    api_publish_url,
    api_version_restore_url,
)


@pytest.mark.django_db
class TestSuperUserPermissions:
    """Tests that only superusers can create, edit, delete, autosave, publish
    and restore posts."""

    def setup_method(self):
        self.client = Client()

    def test_non_superuser_cannot_create_post(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps({"title": "Test", "content": "Content"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_superuser_can_create_post(self):
        user = SuperUserFactory()
        self.client.force_login(user)
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps({"title": "Test", "content": "Content"}),
            content_type="application/json",
        )
        assert response.status_code == 201

    def test_non_superuser_cannot_update_post(self):
        user = UserFactory()
        post = PostFactory(author=user, status=Post.STATUS_DRAFT)
        self.client.force_login(user)
        response = self.client.patch(
            api_post_url(post.slug),
            data=json.dumps({"title": "Updated"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_superuser_can_update_own_draft_post(self):
        user = SuperUserFactory()
        post = PostFactory(author=user, status=Post.STATUS_DRAFT)
        self.client.force_login(user)
        response = self.client.patch(
            api_post_url(post.slug),
            data=json.dumps({"title": "Updated"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_non_superuser_cannot_delete_post(self):
        user = UserFactory()
        post = PostFactory(author=user)
        self.client.force_login(user)
        response = self.client.delete(api_post_url(post.slug))
        assert response.status_code == 403

    def test_superuser_can_delete_own_post(self):
        user = SuperUserFactory()
        post = PostFactory(author=user)
        self.client.force_login(user)
        response = self.client.delete(api_post_url(post.slug))
        assert response.status_code == 204

    def test_non_superuser_cannot_autosave(self):
        user = UserFactory()
        post = PostFactory(author=user)
        self.client.force_login(user)
        response = self.client.patch(
            api_autosave_url(post.slug),
            data=json.dumps({"draft_title": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_superuser_can_autosave(self):
        user = SuperUserFactory()
        post = PostFactory(author=user)
        self.client.force_login(user)
        response = self.client.patch(
            api_autosave_url(post.slug),
            data=json.dumps({"draft_title": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_non_superuser_cannot_publish(self):
        user = UserFactory()
        post = PostFactory(
            author=user,
            status=Post.STATUS_DRAFT,
            draft_title="Test",
            has_draft=True,
        )
        self.client.force_login(user)
        response = self.client.post(
            api_publish_url(post.slug),
            content_type="application/json",
        )
        assert response.status_code == 403

    def test_superuser_can_publish(self):
        user = SuperUserFactory()
        post = PostFactory(
            author=user,
            status=Post.STATUS_DRAFT,
            draft_title="Test",
            has_draft=True,
        )
        self.client.force_login(user)
        response = self.client.post(
            api_publish_url(post.slug),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_non_superuser_cannot_restore_version(self):
        user = UserFactory()
        post = PostFactory(author=user, status=Post.STATUS_PUBLISHED)
        PostVersionFactory(post=post, version_number=1)
        self.client.force_login(user)
        response = self.client.post(api_version_restore_url(post.slug, 1))
        assert response.status_code == 403

    def test_superuser_can_restore_version(self):
        user = SuperUserFactory()
        post = PostFactory(author=user, status=Post.STATUS_PUBLISHED)
        PostVersionFactory(post=post, version_number=1)
        self.client.force_login(user)
        response = self.client.post(api_version_restore_url(post.slug, 1))
        assert response.status_code == 200

    def test_me_endpoint_returns_is_superuser_true(self):
        user = SuperUserFactory()
        self.client.force_login(user)
        response = self.client.get("/api/accounts/me/")
        assert response.status_code == 200
        assert response.json()["is_superuser"] is True

    def test_me_endpoint_returns_is_superuser_false(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get("/api/accounts/me/")
        assert response.status_code == 200
        assert response.json()["is_superuser"] is False

    def test_non_superuser_can_still_read_posts(self):
        """Non-superusers can still view published posts (GET)."""
        post = PostFactory(status=Post.STATUS_PUBLISHED)
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(api_post_url(post.slug))
        assert response.status_code == 200

    def test_anonymous_can_still_read_posts(self):
        """Anonymous users can still view published posts (GET)."""
        post = PostFactory(status=Post.STATUS_PUBLISHED)
        response = self.client.get(api_post_url(post.slug))
        assert response.status_code == 200
