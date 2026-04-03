import factory

from apps.accounts.tests.factories import UserFactory
from apps.blog.models import Comment, Post


SAMPLE_BLOCKNOTE_CONTENT = [
    {
        "id": "1",
        "type": "paragraph",
        "props": {
            "textColor": "default",
            "backgroundColor": "default",
            "textAlignment": "left",
        },
        "content": [
            {
                "type": "text",
                "text": "Contenu de test pour l'article.",
                "styles": {},
            }
        ],
        "children": [],
    }
]


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Sequence(lambda n: f"Article {n}")
    content = factory.LazyFunction(lambda: list(SAMPLE_BLOCKNOTE_CONTENT))
    author = factory.SubFactory(UserFactory)
    status = Post.STATUS_PUBLISHED


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    content = factory.Faker("paragraph", nb_sentences=3, locale="fr_FR")
