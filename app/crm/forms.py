from crm.models import Client, Files
from django import forms


class DateForm(forms.Form):
    start = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    end = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )


CHOICES = [
    (client["name"], client["name"]) for client in Client.objects.all().values("name")
]


class ClientForm(forms.Form):
    CHOICES.append(
        ("all", "all"),
    )
    client = forms.ChoiceField(choices=sorted(CHOICES, key=lambda tup: tup[0]))


class PDFForm(forms.Form):
    FILES_CHOICE = [
        (str(file["uuid"]), file["file_name"])
        for file in Files.objects.all().values("file_name", "uuid")
    ]
    files = forms.MultipleChoiceField(
        choices=FILES_CHOICE, widget=forms.CheckboxSelectMultiple()
    )
    send_to = forms.EmailField()
    message = forms.CharField()
    subject = forms.CharField()
