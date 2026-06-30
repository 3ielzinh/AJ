import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


User = get_user_model()
USERNAME_PATTERN = re.compile(r"^[a-z]+\.[a-z]+$")


class SignUpForm(forms.Form):
    nome = forms.CharField(
        label="Nome",
        max_length=150,
    )
    username = forms.CharField(
        label="Nome de usuario",
        max_length=150,
        help_text="Use o formato nome.sobrenome em letras minusculas.",
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        strip=False,
    )

    def clean_username(self):
        username = self.cleaned_data["username"].strip().lower()
        if not USERNAME_PATTERN.match(username):
            raise forms.ValidationError("Use o formato nome.sobrenome (ex: joao.silva).")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nome de usuario ja esta em uso.")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        try:
            validate_password(password)
        except ValidationError as exc:
            raise forms.ValidationError(exc.messages)
        return password

    def save(self):
        nome = self.cleaned_data["nome"].strip()
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]

        user = User(username=username)
        user.first_name = nome
        user.set_password(password)
        user.save()
        return user
