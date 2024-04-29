# Generated by Django 4.2.11 on 2024-04-28 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("business", "0020_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="searchrecord",
            name="related_papers",
            field=models.ManyToManyField(
                blank=True, related_name="related_search_record", to="business.paper"
            ),
        ),
    ]