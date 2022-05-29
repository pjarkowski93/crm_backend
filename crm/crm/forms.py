from django import forms

from crm.models import Client


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
