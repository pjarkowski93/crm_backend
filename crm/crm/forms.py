from django import forms


class DateForm(forms.Form):
    start = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
    end = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), required=False
    )
