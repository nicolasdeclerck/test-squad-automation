from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0009_add_is_pinned_to_post"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="view_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
