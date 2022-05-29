# Generated by Django 4.0.4 on 2022-05-28 08:45

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=15)),
                ('address_line', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('nip', models.IntegerField()),
                ('created_date', models.DateField(auto_now_add=True)),
                ('created_by', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client_created_by', to=settings.AUTH_USER_MODEL)),
                ('trader', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'client',
                'permissions': [('can_view_only_my_clients', 'Can view only my clients'), ('can_view_my_group_clients', 'Can view my goup clients'), ('can_view_all_clients', 'Can view all clients')],
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('currency', models.CharField(choices=[('PLN', 'PLN'), ('USD', 'USD'), ('EUR', 'EUR')], max_length=3)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.client')),
            ],
            options={
                'db_table': 'sale',
                'permissions': [('can_view_only_my_sales', 'Can view only my sales'), ('can_view_my_group_sales', 'Can view my goup sales'), ('can_view_all_sales', 'Can view all sales')],
            },
        ),
        migrations.CreateModel(
            name='Roadmap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('planned_amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('target_date', models.DateField()),
                ('created_date', models.DateField(auto_now_add=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.client')),
            ],
            options={
                'db_table': 'Roadmap',
                'permissions': [('can_view_only_my_roadmaps', 'Can view only my roadmaps'), ('can_view_my_group_roadmaps', 'Can view my goup roadmaps'), ('can_view_all_roadmaps', 'Can view all roadmaps')],
            },
        ),
    ]