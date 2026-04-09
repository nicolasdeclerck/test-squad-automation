import json

import pytest
from django.test import Client

from apps.accounts.tests.factories import SuperUserFactory, UserFactory
from apps.blog.models import Post, Tag

from .factories import PostFactory, TagFactory
from .helpers import (
    API_POSTS_URL,
    API_TAGS_URL,
    api_autosave_url,
    api_post_url,
    api_publish_url,
)


@pytest.mark.django_db
class TestTagModel:
    def test_tag_str(self):
        tag = TagFactory(name="Python")
        assert str(tag) == "Python"

    def test_tag_slug_auto_generated(self):
        tag = Tag.objects.create(name="Machine Learning")
        assert tag.slug == "machine-learning"

    def test_tag_unique_name(self):
        TagFactory(name="django")
        with pytest.raises(Exception):
            TagFactory(name="django")

    def test_post_tags_m2m(self):
        post = PostFactory()
        tag1 = TagFactory(name="python")
        tag2 = TagFactory(name="django")
        post.tags.add(tag1, tag2)
        assert post.tags.count() == 2
        assert tag1 in post.tags.all()


@pytest.mark.django_db
class TestTagListAPI:
    def setup_method(self):
        self.client = Client()

    def test_list_tags_empty(self):
        response = self.client.get(API_TAGS_URL)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_tags_returns_all(self):
        TagFactory(name="python")
        TagFactory(name="django")
        response = self.client.get(API_TAGS_URL)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_search_tags(self):
        TagFactory(name="python")
        TagFactory(name="django")
        TagFactory(name="pytorch")
        response = self.client.get(API_TAGS_URL + "?search=pyt")
        data = response.json()
        assert len(data) == 2
        names = [t["name"] for t in data]
        assert "python" in names
        assert "pytorch" in names

    def test_search_tags_limit_5(self):
        for i in range(10):
            TagFactory(name=f"test-{i}")
        response = self.client.get(API_TAGS_URL + "?search=test")
        data = response.json()
        assert len(data) == 5


@pytest.mark.django_db
class TestPostCreateWithTags:
    def setup_method(self):
        self.client = Client()
        self.user = SuperUserFactory()
        self.client.force_login(self.user)

    def test_create_post_with_tags(self):
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps(
                {"title": "Test Article", "content": "Content", "tags": ["python", "django"]}
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        tag_names = [t["name"] for t in data["tags"]]
        assert "python" in tag_names
        assert "django" in tag_names
        assert Tag.objects.count() == 2

    def test_create_post_without_tags(self):
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps({"title": "Test Article", "content": "Content"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["tags"] == []

    def test_create_post_reuses_existing_tags(self):
        TagFactory(name="python")
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps(
                {"title": "Test", "content": "Content", "tags": ["python", "django"]}
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        assert Tag.objects.count() == 2  # python reused, django created

    def test_create_post_tags_case_insensitive(self):
        TagFactory(name="Python")
        response = self.client.post(
            API_POSTS_URL,
            data=json.dumps(
                {"title": "Test", "content": "Content", "tags": ["python"]}
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        assert Tag.objects.count() == 1  # reuses existing "Python"


@pytest.mark.django_db
class TestPostDetailWithTags:
    def setup_method(self):
        self.client = Client()

    def test_detail_includes_tags(self):
        tag = TagFactory(name="python")
        post = PostFactory()
        post.tags.add(tag)
        response = self.client.get(api_post_url(post.slug))
        assert response.status_code == 200
        data = response.json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["name"] == "python"

    def test_list_includes_tags(self):
        tag = TagFactory(name="django")
        post = PostFactory()
        post.tags.add(tag)
        response = self.client.get(API_POSTS_URL)
        data = response.json()
        assert data["count"] == 1
        assert len(data["results"][0]["tags"]) == 1
        assert data["results"][0]["tags"][0]["name"] == "django"


@pytest.mark.django_db
class TestPostAutoSaveWithTags:
    def setup_method(self):
        self.client = Client()
        self.user = SuperUserFactory()
        self.client.force_login(self.user)

    def test_autosave_with_tags(self):
        post = PostFactory(author=self.user, status=Post.STATUS_DRAFT)
        response = self.client.patch(
            api_autosave_url(post.slug),
            data=json.dumps(
                {"draft_title": "Updated", "tags": ["python", "django"]}
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.tags.count() == 2

    def test_autosave_updates_tags(self):
        post = PostFactory(author=self.user, status=Post.STATUS_DRAFT)
        tag = TagFactory(name="old-tag")
        post.tags.add(tag)
        response = self.client.patch(
            api_autosave_url(post.slug),
            data=json.dumps({"tags": ["new-tag"]}),
            content_type="application/json",
        )
        assert response.status_code == 200
        post.refresh_from_db()
        assert post.tags.count() == 1
        assert post.tags.first().name == "new-tag"
