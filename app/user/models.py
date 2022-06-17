from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class Department(models.Model):
    uuid = models.UUIDField(default=uuid4)
    name = models.CharField(unique=True, max_length=255)

    def __str__(self) -> str:
        return self.name


class Team(models.Model):
    uuid = models.UUIDField(default=uuid4)
    name = models.CharField(unique=True, max_length=255)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="teams"
    )

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    """
    Extended user model with new fields
    """

    uuid = models.UUIDField(default=uuid4)
    birth_date = models.DateField(null=True)
    team = models.ForeignKey(
        Team, on_delete=models.SET_NULL, related_name="teammates", null=True, blank=True
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        related_name="manages",
        null=True,
        blank=True,
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "user"
