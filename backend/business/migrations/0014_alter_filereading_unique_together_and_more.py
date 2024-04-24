# Generated by Django 4.2.11 on 2024-04-23 16:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("business", "0013_summaryreport"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="filereading",
            unique_together={("user_id", "conversation_path")},
        ),
        migrations.RemoveField(
            model_name="filereading",
            name="file_local_path",
        ),
    ]