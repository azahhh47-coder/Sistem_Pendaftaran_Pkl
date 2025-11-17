from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username / NIP / NISN",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Masukkan Username"
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Masukkan Password"
        })
    )
