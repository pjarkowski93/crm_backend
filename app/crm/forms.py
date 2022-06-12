from crm.models import Client, Files
from django import forms
from django.db import connection

all_tables = connection.introspection.table_names()


def get_client_choices():
    choices = [("all", "all")]
    if "client" in all_tables:
        if Client.objects.all().exists():
            for client in Client.objects.all().values("name"):
                choices.append((client["name"], client["name"]))
    return choices


def get_files_choices():
    choices = []
    if "crm_files" in all_tables:
        if Files.objects.all().exists():
            for file in Files.objects.all().values("uuid", "file_name"):
                choices.append((str(file["uuid"]), file["file_name"]))
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


class PDFForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["files"].choices = get_files_choices()

    files = forms.MultipleChoiceField(
        choices=get_files_choices(), widget=forms.CheckboxSelectMultiple()
    )
    send_to = forms.EmailField()
    message = forms.CharField()
    subject = forms.CharField()
