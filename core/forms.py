from django import forms
from django.contrib.auth.models import User
from .models import BuildingType, GameSettings, ResourceType, UnitType


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

class GameSettingsForm(forms.ModelForm):
    class Meta:
        model = GameSettings
        fields = ['building_growth_factor', 'production_speed_multiplier']

class DynamicJSONFormMixin:
    """
    Mixin to dynamically build form fields from a JSON dictionary and ResourceType models.
    """
    def _build_dynamic_fields(self, field_name, available_keys, default_val=0):
        # field_name usually is 'cost' or 'production'
        json_data = getattr(self.instance, field_name, {}) or {}
        
        for key in available_keys:
            form_field_name = f"{field_name}_{key}"
            self.fields[form_field_name] = forms.IntegerField(
                required=False,
                initial=json_data.get(key, default_val),
                label=f"{field_name.title()} - {key}",
                min_value=0
            )
            
    def _save_dynamic_fields(self, field_name, available_keys):
        json_data = {}
        for key in available_keys:
            form_field_name = f"{field_name}_{key}"
            val = self.cleaned_data.get(form_field_name)
            if val is not None and val > 0:
                json_data[key] = val
        setattr(self.instance, field_name, json_data)

class BuildingTypeForm(forms.ModelForm, DynamicJSONFormMixin):
    class Meta:
        model = BuildingType
        fields = ['name', 'category']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        resources = ResourceType.objects.values_list('name', flat=True)
        self._build_dynamic_fields('cost', resources)
        self._build_dynamic_fields('production', resources)
        
    def save(self, commit=True):
        resources = ResourceType.objects.values_list('name', flat=True)
        self._save_dynamic_fields('cost', resources)
        self._save_dynamic_fields('production', resources)
        return super().save(commit)

class UnitTypeForm(forms.ModelForm, DynamicJSONFormMixin):
    class Meta:
        model = UnitType
        fields = ['name', 'category']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        resources = ResourceType.objects.values_list('name', flat=True)
        self._build_dynamic_fields('cost', resources)
        
        # Stats fields
        stats = getattr(self.instance, 'stats', {}) or {}
        for stat_key in ['attack', 'defense', 'cargo', 'spy']:
            if stat_key == 'spy':
                self.fields[f"stats_{stat_key}"] = forms.BooleanField(
                    required=False,
                    initial=stats.get(stat_key, False),
                    label="Is Spy Unit?"
                )
            else:
                self.fields[f"stats_{stat_key}"] = forms.IntegerField(
                    required=False,
                    initial=stats.get(stat_key, 0),
                    label=f"Stat - {stat_key.title()}",
                    min_value=0
                )
        
    def save(self, commit=True):
        resources = ResourceType.objects.values_list('name', flat=True)
        self._save_dynamic_fields('cost', resources)
        
        # Save Stats
        stats = {}
        for stat_key in ['attack', 'defense', 'cargo']:
            val = self.cleaned_data.get(f"stats_{stat_key}")
            if val is not None and val > 0:
                stats[stat_key] = val
                
        spy_val = self.cleaned_data.get("stats_spy")
        if spy_val:
            stats["spy"] = True
            
        self.instance.stats = stats
        return super().save(commit)
