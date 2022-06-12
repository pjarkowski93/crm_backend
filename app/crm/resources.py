from typing import Any, Dict

from crm.models import Client, Sale
from django.contrib.auth import get_user_model
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

User = get_user_model()


class SaleResource(resources.ModelResource):
    class ClientForeignKeyWiget(ForeignKeyWidget):
        def get_queryset(self, value: str, row: Dict[str, Any], **kwargs) -> Sale:
            return self.model.objects.filter(name=value)

    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=ForeignKeyWidget(Client, field="name"),
    )

    class Meta:
        model = Sale
        import_id_fields = ("external_id",)
        fields = (
            "amount",
            "currency",
            "client",
            "brand",
            "external_id",
            "sale_date_from",
            "sale_date_to",
        )
        skip_unchanged = True


class ClientResource(resources.ModelResource):
    class TraderForeignKeyWiget(ForeignKeyWidget):
        def get_queryset(self, value: str, row: Dict[str, Any], **kwargs) -> Sale:
            return self.model.objects.filter(email=value)

    trader = fields.Field(
        column_name="trader",
        attribute="trader",
        widget=ForeignKeyWidget(User, field="email"),
    )

    class Meta:
        model = Client
        import_id_fields = ("nip", "name")
        skip_unchanged = True
        exclude = ("id", "uuid", "created_date")
