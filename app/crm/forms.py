from datetime import datetime

from crm.models import Sale
from crm.widgets import DatePickerInput, DateTimePickerInput, TimePickerInput
from django import forms
from django.db import connection

all_tables = connection.introspection.table_names()


class DateTimeWidget(forms.DateTimeInput):
    class Media:
        js = ("js/jquery-ui-timepicker-addon.js",)

    def __init__(self, attrs=None):
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {"class": "datetimepicker"}


def get_client_choices():
    choices = [("all", "all")]
    existed_sale_clients = {}
    if "client" in all_tables and "sale" in all_tables:
        if Sale.objects.all().exists():
            for sale in Sale.objects.all():
                existed_sale_clients.update({sale.client.name: sale.client.name})
    for client_name in existed_sale_clients:
        choices.append((client_name, client_name))
    return choices


class DateForm(forms.Form):
    start = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    end = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )


class ClientForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["client"].choices = get_client_choices()

    client = forms.ChoiceField(
        choices=sorted(get_client_choices(), key=lambda tup: tup[0])
    )


class DateTimeForm(forms.Form):
    my_date_field = forms.DateField(
        widget=DatePickerInput, label="Data zapisu pliku", required=False
    )
    my_time_field = forms.TimeField(
        widget=TimePickerInput, label="Godzina zapisu pliku", required=False
    )


class PDFForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    files = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(),
        label="Zapisane pliki",
    )
    send_to = forms.EmailField()
    message = forms.CharField()
    subject = forms.CharField()
