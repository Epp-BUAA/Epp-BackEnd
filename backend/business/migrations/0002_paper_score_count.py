# Generated by Django 4.2.11 on 2024-04-11 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("business", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="paper",
            name="score_count",
            field=models.IntegerField(default=0),
        ),
    ]
