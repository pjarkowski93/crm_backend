from typing import Union

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from crm.models import Client, Roadmap, Sale


@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_filter = ("name", "country", "city", "nip")
    list_display: Union[list, tuple] = (
        "uuid",
        "name",
        "country",
        "city",
        "email",
        "nip",
    )


@admin.register(Sale)
class SaleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display: Union[list, tuple] = (
        "uuid",
        "get_client",
        "get_trader",
        "amount",
        "currency",
        "created_date",
        "brand",
    )
    list_filter = ("created_date", "currency", "client__trader__email", "brand")

    @admin.display(ordering="client__name", description="Client")
    def get_client(self, sale_obj):
        return sale_obj.client.name

    @admin.display(ordering="client__trader__email", description="Trader")
    def get_trader(self, sale_obj):
        return sale_obj.client.trader.email


@admin.register(Roadmap)
class RoadmapAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display: Union[list, tuple] = (
        "uuid",
        "get_client",
        "planned_amount",
        "target_date",
    )

    @admin.display(ordering="client__name", description="Client")
    def get_client(self, roadmap_obj):
        return roadmap_obj.client.email
