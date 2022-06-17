from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.forms import FileField

User = get_user_model()

# Create your models here.


class Client(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True)
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    nip = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    trader = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="client"
    )
    created_date = models.DateField(auto_now_add=True)
    external_id = models.UUIDField(unique=True, null=True, blank=True)

    class Meta:
        db_table = "client"
        permissions = [
            ("can_view_only_my_clients", "Can view only my clients"),
            ("can_create_only_my_clients", "Can create only my clients"),
            ("can_update_only_my_clients", "Can update only my clients"),
            ("can_delete_only_my_clients", "Can delete only my clients"),
            ("can_view_my_group_clients", "Can view my goup clients"),
            ("can_create_my_group_clients", "Can create my goup clients"),
            ("can_update_my_group_clients", "Can update my goup clients"),
            ("can_delete_my_group_clients", "Can delete my goup clients"),
            ("can_view_department_clients", "Can view department clients"),
            ("can_create_department_clients", "Can create department clients"),
            ("can_update_department_clients", "Can update department clients"),
            ("can_delete_department_clients", "Can delete department clients"),
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
    sale_date_from = models.DateField(null=True, blank=True)
    sale_date_to = models.DateField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    external_id = models.UUIDField(unique=True, null=True, blank=True)

    class Meta:
        db_table = "sale"
        permissions = [
            ("can_view_only_my_sales", "Can view only my sales"),
            ("can_create_only_my_sales", "Can create only my sales"),
            ("can_update_only_my_sales", "Can update only my sales"),
            ("can_delete_only_my_sales", "Can delete only my sales"),
            ("can_view_my_group_sales", "Can view my goup sales"),
            ("can_create_my_group_sales", "Can create my goup sales"),
            ("can_update_my_group_sales", "Can update my goup sales"),
            ("can_delete_my_group_sales", "Can delete my goup sales"),
            ("can_view_department_sales", "Can view department sales"),
            ("can_create_department_sales", "Can create department sales"),
            ("can_update_department_sales", "Can update department sales"),
            ("can_delete_department_sales", "Can delete department sales"),
        ]

    def save(self, *args, **kwargs) -> None:
        MONTHS = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }
        if not self.pk or not self.months.all().exists():
            super().save(*args, **kwargs)
            to_save = []
            _divaded_by = 0
            for month in range(self.sale_date_from.month, self.sale_date_to.month):
                _divaded_by += 1
            for month in range(self.sale_date_from.month, self.sale_date_to.month):
                to_save.append(
                    SaleMonths.objects.update_or_create(
                        sale=self,
                        sale_month=MONTHS[month],
                        sale_month_amount=self.amount / _divaded_by,
                    )
                )
        else:
            return super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale ({self.client.name} - {self.brand})"


class SaleMonths(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True)
    sale = models.ForeignKey(
        Sale, on_delete=models.SET_NULL, null=True, related_name="months"
    )
    sale_month_amount = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    sale_month = models.CharField(max_length=10)


class Roadmap(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    planned_amount = models.DecimalField(max_digits=20, decimal_places=2)
    target_date = models.DateField()
    created_date = models.DateField(auto_now_add=True)
    external_id = models.UUIDField(unique=True, null=True, blank=True)

    class Meta:
        db_table = "Roadmap"
        permissions = [
            ("can_view_only_my_roadmaps", "Can view only my roadmaps"),
            ("can_create_only_my_roadmaps", "Can create only my roadmaps"),
            ("can_update_only_my_roadmaps", "Can update only my roadmaps"),
            ("can_delete_only_my_roadmaps", "Can delete only my roadmaps"),
            ("can_view_my_group_roadmaps", "Can view my goup roadmaps"),
            ("can_create_my_group_roadmaps", "Can create my goup roadmaps"),
            ("can_update_my_group_roadmaps", "Can update my goup roadmaps"),
            ("can_delete_my_group_roadmaps", "Can delete my goup roadmaps"),
            ("can_view_department_roadmaps", "Can view department roadmaps"),
            ("can_create_department_roadmaps", "Can create department roadmaps"),
            ("can_update_department_roadmaps", "Can update department roadmaps"),
            ("can_delete_department_roadmaps", "Can delete department roadmaps"),
        ]

    def __str__(self) -> str:
        return f"Roadmap ({self.client.name})"


class Files(models.Model):
    uuid = models.UUIDField(default=uuid4, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="files"
    )
    file = FileField(max_length=255)
    file_name = models.CharField(max_length=255)
    path_to_file = models.CharField(max_length=255)
    created_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
