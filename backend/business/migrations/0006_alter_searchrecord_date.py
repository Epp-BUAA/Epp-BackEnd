# Generated by Django 4.2.11 on 2024-04-16 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("business", "0005_alter_filereading_conversation_path_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="searchrecord",
            name="date",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
