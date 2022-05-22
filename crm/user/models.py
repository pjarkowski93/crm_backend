from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    """
    Extended user model with new fields
    """

    email = models.EmailField(unique=True)
    uuid = models.UUIDField(default=uuid4)
    birth_date = models.DateField(null=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "user"
