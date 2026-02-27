from django import forms
from django.contrib.auth.models import User


class UserRegistrationForm(forms.Form):
    """Form for new user registration: username, name, password."""

    username = forms.CharField(
        max_length=150,
        label="Usuario",
        widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}),
    )
    first_name = forms.CharField(
        max_length=150,
        label="Nombre",
        required=False,
        widget=forms.TextInput(attrs={"autocomplete": "given-name"}),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Repetir contraseña",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_username(self) -> str:
        username = self.cleaned_data.get("username", "").strip()
        if not username:
            raise forms.ValidationError("El usuario es obligatorio.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username

    def clean(self) -> dict[str, str]:
        data = super().clean()
        if data is None:
            return {}
        p1 = data.get("password1")
        p2 = data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError({"password2": "Las contraseñas no coinciden."})
        return data
