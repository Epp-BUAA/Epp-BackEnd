# Generated by Django 4.2.11 on 2024-05-28 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0034_alter_abstractreport_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstractreport',
            name='status',
            field=models.CharField(choices=[('P', '未生成'), ('IP', '生成中'), ('C', '已生成'), ('T', '超时')], default='P', max_length=2),
        ),
    ]