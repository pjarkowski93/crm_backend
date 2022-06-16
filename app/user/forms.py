from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from user.models import Team

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    team = forms.ModelChoiceField(Team.objects, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "team", "password1", "password2"]
