import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

import phonenumbers
from crm.models import Client, Files, Sale
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage

User = get_user_model()


class StatusEnum(Enum):
    FAILED = "niepowodzenie"
    UPDATED = "zaktualizowany"
    CREATED = "utworzony"
    SKIPED = "pominięty"


@dataclass
class ImportSaleDataClass:
    client: Optional[str]
    amount: Optional[str]
    currency: Optional[str]
    brand: Optional[str]
    sale_date_from: Optional[str]
    sale_date_to: Optional[str]
    external_id: Optional[UUID]
    status: Optional[str]
    errors: Optional[str]
    updated_fields: Optional[str]

    def to_dict(self) -> Dict:
        return {
            "client": self.client,
            "amount": self.amount,
            "currency": self.currency,
            "brand": self.brand,
            "sale_date_from": self.sale_date_from,
            "sale_date_to": self.sale_date_to,
            "external_id": self.external_id,
            "status": self.status,
            "errors": self.errors,
            "updated_fields": self.updated_fields,
        }


@dataclass
class ImportClientDataClass:
    name: Optional[str]
    country: Optional[str]
    phone_number: Optional[str]
    address_line: Optional[str]
    city: Optional[str]
    email: Optional[str]
    nip: Optional[str]
    trader: Optional[str]
    status: Optional[str]
    errors: Optional[str]
    updated_fields: Optional[str]

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "country": self.country,
            "phone_number": self.phone_number,
            "address_line": self.address_line,
            "city": self.city,
            "email": self.email,
            "nip": self.nip,
            "trader": self.trader,
            "status": self.status,
            "errors": self.errors,
            "updated_fields": self.updated_fields,
        }


class EmailSender:
    def send(
        self,
        recipient: str,
        message: str,
        subject: str,
        files: Optional[List[Files]] = [],
    ):
        mail = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient],
        )
        for file in files:
            mail.attach_file(file.path_to_file)
        mail.send()


class BaseImport:
    def __init__(self) -> None:
        self.errors = []
        self.updated = []
        self.skiped = []
        self.created = []
        self.results = {}
        self.row_errors = []

    @property
    def _required_keys(self) -> set:
        raise NotImplementedError

    def _import(self, row: Dict[str, Any]) -> None:
        raise NotImplementedError

    def _create(self, row: Dict[str, Any]) -> None:
        raise NotImplementedError

    def _update_or_skip(self, row: Dict[str, Any]) -> None:
        raise NotImplementedError

    def _add_to_created(self, row: Dict[str, Any]) -> None:
        raise NotImplementedError

    def _add_to_updated(self, row: Dict[str, Any], updated_fields: List[str]) -> None:
        raise NotImplementedError

    def _add_to_skiped(self, row: Dict[str, Any]) -> None:
        raise NotImplementedError

    def validate_keys(self, row: Dict[str, Any]) -> bool:
        self.row_errors = []
        row_keys = set(row.keys())
        if row_keys != self._required_keys:
            for required_key in self._required_keys:
                if required_key not in row_keys:
                    self.row_errors.append(f"Brak kolumny {required_key}")
        if self.row_errors:
            return False
        return True

    def validate_row_data(self, row: Dict[str, Any]) -> bool:
        raise NotImplementedError

    def import_data(self, data_to_import: List[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError


class ImportSales(BaseImport):
    @property
    def _required_keys(self) -> set:
        return {
            "client",
            "amount",
            "currency",
            "brand",
            "sale_date_from",
            "sale_date_to",
            "external_id",
        }

    def validate_row_data(self, row: Dict[str, Any]) -> bool:
        self.row_errors = []
        current_date = datetime.date.today()

        try:
            Client.objects.get(name=row["client"])
        except Client.DoesNotExist:
            self.row_errors.append(f"Klient ({row['client']}) nie istnieje")
        except Client.MultipleObjectsReturned:
            self.row_errors.append(
                f"Istnieje więcej niż jeden klient o podanej nazwie ({row['client']})"
            )
        if (
            row["sale_date_from"].date() > current_date
            and row["sale_date_to"].date() > current_date
        ):
            self.row_errors.append(
                (
                    "Data sprzedaży nie może być przyszłościowa "
                    f"({row['sale_date_from'].date()} - {row['sale_date_to'].date()})"
                )
            )
        try:
            float(row["amount"])
        except ValueError:
            self.row_errors.append(
                f"Amount ({row['amount']}) nie jest wartością numeryczną"
            )
        try:
            UUID(row["external_id"])
        except ValueError:
            self.row_errors.append(
                f"external_id ({row['external_id']}) nie jest formatu uuid"
            )
        if self.row_errors:
            return False
        return True

    def import_data(self, data_to_import: List[Dict[str, Any]]) -> Dict[str, Any]:
        for data in data_to_import:
            if not self.validate_keys(data):
                _not_imported = ImportSaleDataClass(
                    client=data.get("client"),
                    amount=data.get("amount"),
                    currency=data.get("currency"),
                    brand=data.get("brand"),
                    sale_date_from=data.get("sale_date_from"),
                    sale_date_to=data.get("sale_date_to"),
                    external_id=data.get("external_id"),
                    status=StatusEnum.FAILED.value,
                    updated_fields="",
                    errors=",".join(self.row_errors),
                )
                self.errors.append(_not_imported.to_dict())
                return {"errors": self.errors}

            if not self.validate_row_data(data):
                _not_imported = ImportSaleDataClass(
                    client=data["client"],
                    amount=data["amount"],
                    currency=data["currency"],
                    brand=data["brand"],
                    sale_date_from=data["sale_date_from"],
                    sale_date_to=data["sale_date_to"],
                    external_id=data["external_id"],
                    status=StatusEnum.FAILED.value,
                    updated_fields="",
                    errors=",".join(self.row_errors),
                )
                self.errors.append(_not_imported.to_dict())
            self._import(data)
            self.results["created"] = self.created
            self.results["updated"] = self.updated
            self.results["skiped"] = self.skiped
            self.results["errors"] = self.errors
        return self.results

    def _import(self, row: Dict[str, Any]) -> None:
        if Sale.objects.filter(external_id=row["external_id"]).exists():
            return self._update_or_skip(row)
        return self._create(row)

    def _create(self, row: Dict[str, Any]) -> None:
        Sale.objects.create(
            client=client,
            amount=row["amount"],
            currency=row["currency"],
            brand=row["brand"],
            sale_date_from=row["sale_date_from"],
            sale_date_to=row["sale_date_to"],
            external_id=row["external_id"],
        )
        return self._add_to_created(row)

    def _update_or_skip(self, row: Dict[str, Any]) -> None:
        updated_fields = []
        sale_obj = Sale.objects.filter(external_id=row["external_id"])
        for sale in sale_obj:
            if sale.amount != row["amount"]:
                updated_fields.append("amount")
            if sale.currency != row["currency"]:
                updated_fields.append("currency")
            if sale.sale_date_from != row["sale_date_from"].date():
                updated_fields.append("sale_date_from")
            if sale.sale_date_to != row["sale_date_to"].date():
                updated_fields.append("sale_date_to")
        if not updated_fields:
            return self._add_to_skiped(row)
        sale_obj.update(
            amount=row["amount"],
            currency=row["currency"],
            sale_date_from=row["sale_date_from"],
            sale_date_to=row["sale_date_to"],
        )
        return self._add_to_updated(row, updated_fields)

    def _add_to_created(self, row: Dict[str, Any]) -> None:
        self.created.append(
            ImportSaleDataClass(
                client=row["client"],
                amount=row["amount"],
                currency=row["currency"],
                brand=row["brand"],
                sale_date_from=row["sale_date_from"],
                sale_date_to=row["sale_date_to"],
                external_id=row["external_id"],
                status=StatusEnum.CREATED.value,
                updated_fields="",
                errors="",
            )
        )

    def _add_to_updated(self, row: Dict[str, Any], updated_fields: List[str]) -> None:
        self.updated.append(
            ImportSaleDataClass(
                client=row["client"],
                amount=row["amount"],
                currency=row["currency"],
                brand=row["brand"],
                sale_date_from=row["sale_date_from"],
                sale_date_to=row["sale_date_to"],
                external_id=row["external_id"],
                status=StatusEnum.UPDATED.value,
                updated_fields=",".join(updated_fields),
                errors="",
            )
        )

    def _add_to_skiped(self, row: Dict[str, Any]) -> None:
        self.skiped.append(
            ImportSaleDataClass(
                client=row["client"],
                amount=row["amount"],
                currency=row["currency"],
                brand=row["brand"],
                sale_date_from=row["sale_date_from"],
                sale_date_to=row["sale_date_to"],
                external_id=row["external_id"],
                status=StatusEnum.SKIPED.value,
                updated_fields="",
                errors="",
            )
        )


class ImportClient(BaseImport):
    @property
    def _required_keys(self) -> set:
        return {
            "name",
            "country",
            "phone_number",
            "address_line",
            "city",
            "email",
            "nip",
            "trader",
        }

    def validate_row_data(self, row: Dict[str, Any]) -> bool:
        self.row_errors = []

        try:
            User.objects.get(email=row["trader"])
        except User.DoesNotExist:
            self.row_errors.append(f"Sprzedawca ({row['trader']}) nie istnieje")
        except User.MultipleObjectsReturned:
            self.row_errors.append(
                f"Istnieje więcej niż jeden sprzedawca o podanej nazwie ({row['trader']})"
            )
        if len(str(row["nip"])) != 10:
            self.row_errors.append(f"Nieprawidłowy nip ({row['nip']})")
        try:
            phone_number = phonenumbers.parse(row["phone_number"])
            if not phonenumbers.is_valid_number(phone_number):
                self.row_errors.append(
                    f"Nieprawidłowy numer telefonu ({row['phone_number']})"
                )
        except Exception:
            self.row_errors.append(
                f"Nieprawidłowy numer telefonu ({row['phone_number']})"
            )
        if self.row_errors:
            return False
        return True

    def import_data(self, data_to_import: List[Dict[str, Any]]) -> Dict[str, Any]:
        for data in data_to_import:
            if not self.validate_keys(data):
                _not_imported = ImportClientDataClass(
                    name=data.get("name"),
                    country=data.get("country"),
                    phone_number=data.get("phone_number"),
                    address_line=data.get("address_line"),
                    city=data.get("city"),
                    email=data.get("email"),
                    nip=data.get("nip"),
                    trader=data.get("trader"),
                    status=StatusEnum.FAILED.value,
                    errors=",".join(self.row_errors),
                    updated_fields="",
                )
                self.errors.append(_not_imported.to_dict())
                return {"errors": self.errors}

            if not self.validate_row_data(data):
                _not_imported = ImportClientDataClass(
                    name=data["name"],
                    country=data["country"],
                    phone_number=data["phone_number"],
                    address_line=data["address_line"],
                    city=data["city"],
                    email=data["email"],
                    nip=data["nip"],
                    trader=data["trader"],
                    status=StatusEnum.FAILED.value,
                    errors=",".join(self.row_errors),
                    updated_fields="",
                )
                self.errors.append(_not_imported.to_dict())
            self._import(data)
            self.results["created"] = self.created
            self.results["updated"] = self.updated
            self.results["skiped"] = self.skiped
            self.results["errors"] = self.errors
        return self.results

    def _import(self, row: Dict[str, Any]) -> None:
        if Client.objects.filter(nip=row["nip"]).exists():
            return self._update_or_skip(row)
        return self._create(row)

    def _create(self, row: Dict[str, Any]) -> None:
        user = User.objects.get(email=row["trader"])
        if Client.objects.filter(email=row["email"]).exists():
            _not_imported = ImportClientDataClass(
                name=row["name"],
                country=row["country"],
                phone_number=row["phone_number"],
                address_line=row["address_line"],
                city=row["city"],
                email=row["email"],
                nip=row["nip"],
                trader=row["trader"],
                status=StatusEnum.FAILED.value,
                errors=f"Klient z takim adresem email {row['email']} już istnieje",
                updated_fields="",
            )
            self.errors.append(_not_imported.to_dict())
            return
        Client.objects.create(
            name=row["name"],
            country=row["country"],
            phone_number=row["phone_number"],
            address_line=row["address_line"],
            city=row["city"],
            email=row["email"],
            nip=row["nip"],
            trader=user,
        )

        return self._add_to_created(row)

    def _update_or_skip(self, row: Dict[str, Any]) -> None:
        updated_fields = []
        client_obj = Client.objects.filter(nip=row["nip"])
        for client in client_obj:
            if client.name != row["name"]:
                updated_fields.append("name")
            if client.country != row["country"]:
                updated_fields.append("country")
            if client.phone_number != row["phone_number"]:
                updated_fields.append("phone_number")
            if client.address_line != row["address_line"]:
                updated_fields.append("address_line")
            if client.city != row["city"]:
                updated_fields.append("city")
            if client.email != row["email"]:
                updated_fields.append("email")
        if not updated_fields:
            return self._add_to_skiped(row)
        client_obj.update(
            name=row["name"],
            country=row["country"],
            phone_number=row["phone_number"],
            address_line=row["address_line"],
            city=row["city"],
            email=row["email"],
        )
        return self._add_to_updated(row, updated_fields)

    def _add_to_created(self, row: Dict[str, Any]) -> None:
        self.created.append(
            ImportClientDataClass(
                name=row["name"],
                country=row["country"],
                phone_number=row["phone_number"],
                address_line=row["address_line"],
                city=row["city"],
                email=row["email"],
                nip=row["nip"],
                trader=row["trader"],
                status=StatusEnum.CREATED.value,
                errors="",
                updated_fields="",
            )
        )

    def _add_to_updated(self, row: Dict[str, Any], updated_fields: List[str]) -> None:
        self.updated.append(
            ImportClientDataClass(
                name=row["name"],
                country=row["country"],
                phone_number=row["phone_number"],
                address_line=row["address_line"],
                city=row["city"],
                email=row["email"],
                nip=row["nip"],
                trader=row["trader"],
                status=StatusEnum.UPDATED.value,
                errors="",
                updated_fields=",".join(updated_fields),
            )
        )

    def _add_to_skiped(self, row: Dict[str, Any]) -> None:
        self.skiped.append(
            ImportClientDataClass(
                name=row["name"],
                country=row["country"],
                phone_number=row["phone_number"],
                address_line=row["address_line"],
                city=row["city"],
                email=row["email"],
                nip=row["nip"],
                trader=row["trader"],
                status=StatusEnum.SKIPED.value,
                errors="",
                updated_fields="",
            )
        )
