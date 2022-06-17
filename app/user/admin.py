from typing import Union

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "uuid",
        "email",
        "first_name",
        "last_name",
        "birth_date",
        "is_staff",
        "is_active",
    )
    list_filter: Union[list, tuple] = ("is_staff", "is_active")
