import factory
from django.utils import timezone

from apps.accounts.tests.factories import UserFactory
from apps.blog.models import Comment, Post


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
