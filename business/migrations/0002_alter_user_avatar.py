# Generated by Django 4.2.11 on 2024-04-11 19:36

import business.utils.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("business", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                default="uploads/users/avatars/default.jpg",
                null=True,
                storage=business.utils.storage.ImageStorage(),
                upload_to="uploads/users/avatars/",
            ),
        ),
    ]