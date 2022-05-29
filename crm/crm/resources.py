from typing import Any, Dict

from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from crm.models import Client, Sale


class SaleResource(resources.ModelResource):
    class ClientForeignKeyWiget(ForeignKeyWidget):
        def get_queryset(self, value: str, row: Dict[str, Any], **kwargs) -> Sale:
            return self.model.objects.filter(name=value)

    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=ForeignKeyWidget(Client, field="name"),
    )

    def skip_row(self, instance, original):
        skip = Sale.objects.filter(
            currency=instance.currency,
            client=instance.client,
            brand=instance.brand,
            sale_date_from=instance.sale_date_from,
            sale_date_to=instance.sale_date_to,
            amount=instance.amount,
        ).exists()
        return skip

    class Meta:
        model = Sale
        import_id_fields = (
            "amount",
            "currency",
            "client",
            "brand",
            "sale_date_from",
            "sale_date_to",
        )
        skip_unchanged = True
        exclude = ("id", "uuid", "created_date")


class ClientResource(resources.ModelResource):
    def skip_row(self, instance, original):
        skip = Client.objects.filter(
            name=instance.name,
            country=instance.country,
            phone_number=instance.phone_number,
            address_line=instance.address_line,
            city=instance.city,
            email=instance.email,
            nip=instance.nip,
        ).exists()
        return skip

    class Meta:
        model = Client
        import_id_fields = (
            "name",
            "country",
            "phone_number",
            "address_line",
            "city",
            "email",
            "nip",
        )
        skip_unchanged = True
        exclude = ("id", "uuid", "created_date")
