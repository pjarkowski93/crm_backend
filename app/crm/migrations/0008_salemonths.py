# Generated by Django 4.0.4 on 2022-06-12 10:38

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0007_client_external_id_roadmap_external_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleMonths',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('sale_month', models.CharField(max_length=10)),
                ('sale', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='months', to='crm.sale')),
            ],
        ),
    ]