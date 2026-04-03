from django.db import migrations, models


def convert_text_to_blocknote(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.all():
        if isinstance(post.content, str) and post.content:
            post.content = [
                {
                    "id": "migrated",
                    "type": "paragraph",
                    "props": {
                        "textColor": "default",
                        "backgroundColor": "default",
                        "textAlignment": "left",
                    },
                    "content": [
                        {"type": "text", "text": post.content, "styles": {}}
                    ],
                    "children": [],
                }
            ]
            post.save(update_fields=["content"])


def convert_blocknote_to_text(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.all():
        if isinstance(post.content, list):
            texts = []
            for block in post.content:
                if isinstance(block, dict):
                    for inline in block.get("content", []):
                        if isinstance(inline, dict):
                            texts.append(inline.get("text", ""))
            post.content = " ".join(texts)
            post.save(update_fields=["content"])


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_comment"),
    ]

    operations = [
        migrations.RunPython(
            convert_text_to_blocknote,
            convert_blocknote_to_text,
        ),
        migrations.AlterField(
            model_name="post",
            name="content",
            field=models.JSONField(default=list),
        ),
    ]
