from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0008_add_cover_image_to_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="is_pinned",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name="post",
            name="pinned_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
