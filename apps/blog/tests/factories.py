import factory
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.blog.models import Comment, Post, PostVersion


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Article {n}")
    content = factory.Faker("paragraph", nb_sentences=5, locale="fr_FR")
    author = factory.SubFactory(UserFactory)
    status = Post.STATUS_PUBLISHED
    published_at = factory.LazyFunction(timezone.now)
    draft_title = ""
    draft_content = ""
    has_draft = False


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker("paragraph", nb_sentences=3, locale="fr_FR")


class PostVersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostVersion

    post = factory.SubFactory(PostFactory)
    version_number = factory.Sequence(lambda n: n + 1)
    title = factory.LazyAttribute(lambda o: o.post.title)
    content = factory.LazyAttribute(lambda o: o.post.content)
    published_at = factory.LazyFunction(timezone.now)
    created_by = factory.LazyAttribute(lambda o: o.post.author)
