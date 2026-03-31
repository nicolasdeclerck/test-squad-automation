import factory
from django.contrib.auth import get_user_model

from apps.blog.models import Category, Comment, Post, Tag

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Catégorie {n}")
    slug = factory.Sequence(lambda n: f"categorie-{n}")


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f"Tag {n}")
    slug = factory.Sequence(lambda n: f"tag-{n}")


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Article {n}")
    slug = factory.Sequence(lambda n: f"article-{n}")
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    content = "<p>Contenu de test</p>"
    content_json = factory.LazyFunction(
        lambda: [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": "Contenu de test"}],
            }
        ]
    )
    status = Post.STATUS_PUBLISHED
    excerpt = "Extrait de test"


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = "Un commentaire de test"
    is_approved = False
