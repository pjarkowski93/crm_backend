from uuid import uuid4

from django.core.validators import MinLengthValidator
from django.db import models
from user.models import User

# Create your models here.


class Client(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    email = models.EmailField()
    nip = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    trader = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="client"
    )
    created_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "client"
        permissions = [
            ("can_view_only_my_clients", "Can view only my clients"),
            ("can_view_my_group_clients", "Can view my goup clients"),
            ("can_view_all_clients", "Can view all clients"),
        ]

    def __str__(self) -> str:
        return f"Client ({self.name} - {self.nip})"


class Sale(models.Model):
    CURRENCY_CHOICES = [
        ("PLN", "PLN"),
        ("USD", "USD"),
        ("EUR", "EUR"),
    ]
    uuid = models.UUIDField(default=uuid4, unique=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    brand = models.CharField(max_length=255, null=True)
    sale_date_from = models.DateField(null=True)
    sale_date_to = models.DateField(null=True)
    created_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "sale"
        permissions = [
            ("can_view_only_my_sales", "Can view only my sales"),
            ("can_view_my_group_sales", "Can view my goup sales"),
            ("can_view_all_sales", "Can view all sales"),
        ]

    def __str__(self):
        return f"Sale ({self.client.name} - {self.brand})"


class Roadmap(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    planned_amount = models.DecimalField(max_digits=20, decimal_places=2)
    target_date = models.DateField()
    created_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "Roadmap"
        permissions = [
            ("can_view_only_my_roadmaps", "Can view only my roadmaps"),
            ("can_view_my_group_roadmaps", "Can view my goup roadmaps"),
            ("can_view_all_roadmaps", "Can view all roadmaps"),
        ]

    def __str__(self) -> str:
        return f"Roadmap ({self.client.name})"
