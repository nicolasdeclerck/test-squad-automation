import json

from django.db import migrations, models


def convert_text_to_json(apps, schema_editor):
    """Convert existing text content to BlockNote JSON format."""
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.all():
        if isinstance(post.content, str) and post.content.strip():
            post.content = [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": post.content}],
                }
            ]
            post.save(update_fields=["content"])
        elif not post.content:
            post.content = []
            post.save(update_fields=["content"])


def convert_json_to_text(apps, schema_editor):
    """Reverse: convert BlockNote JSON back to plain text."""
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.all():
        if isinstance(post.content, list):
            texts = []
            for block in post.content:
                block_texts = _extract_text(block)
                if block_texts:
                    texts.append(block_texts)
            post.content = "\n".join(texts)
            post.save(update_fields=["content"])


def _extract_text(block):
    """Recursively extract text from a BlockNote block."""
    texts = []
    for item in block.get("content", []):
        if item.get("type") == "text":
            texts.append(item.get("text", ""))
        if "children" in item:
            for child in item["children"]:
                texts.append(_extract_text(child))
    return "".join(texts)


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_comment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="content",
            field=models.JSONField(default=list),
        ),
        migrations.RunPython(
            convert_text_to_json,
            reverse_code=convert_json_to_text,
        ),
    ]
