# Generated by Django 4.0.4 on 2022-06-12 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='external_id',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
    ]
