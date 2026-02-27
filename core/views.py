from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_http_methods

from .decorators import game_master_required, is_game_master
from .forms import (
    BuildingTypeForm,
    GameSettingsForm,
    PrivilegedUserCreateForm,
    UnitTypeForm,
    UserRegistrationForm,
)
from .models import (
    BuildingType,
    GameSettings,
    Planet,
    PlanetBuilding,
    PlanetResource,
    PlanetUnit,
    ResourceType,
    UnitType,
)
from .selectors.planet_buildings import get_buildings_info_for_planet
from .services.production import tick_planet_production
from .services.building import upgrade_building


class CustomLoginView(LoginView):
    """Login view that shows a user-facing message on invalid credentials."""

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña inválido.")
        return super().form_invalid(form)


@require_http_methods(["GET", "POST"])
def register(request):
    """Register a new user (username, name, password). Redirects to login on success."""
    if request.user.is_authenticated:
        return redirect("index")
    form = UserRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        User.objects.create_user(
            username=form.cleaned_data["username"].strip(),
            first_name=form.cleaned_data.get("first_name", "").strip() or None,
            password=form.cleaned_data["password1"],
        )
        messages.success(request, "Usuario creado con éxito.")
        return redirect("login")
    return render(request, "registration/register.html", {"form": form})


@login_required
def index(request):
    if is_game_master(request.user):
        return redirect("gm_dashboard")
    try:
        dictator = request.user.dictator_profile
        if dictator.main_planet:
            return redirect("planet_detail", planet_id=dictator.main_planet.id)
    except ObjectDoesNotExist:
        pass
    return render(request, "core/no_planet.html")


def _ensure_planet_resources(planet: Planet) -> dict[str, PlanetResource]:
    """Ensure every ResourceType has a PlanetResource row for this planet.

    Uses bulk_create with ignore_conflicts to avoid N+1 queries.
    Returns a dict mapping resource_type.name → PlanetResource.
    """
    resource_types = list(ResourceType.objects.all())
    existing_names = set(
        PlanetResource.objects.filter(planet=planet).values_list("resource_type__name", flat=True)
    )
    new_rows = [
        PlanetResource(planet=planet, resource_type=rt)
        for rt in resource_types
        if rt.name not in existing_names
    ]
    if new_rows:
        PlanetResource.objects.bulk_create(new_rows, ignore_conflicts=True)

    resources = PlanetResource.objects.filter(planet=planet).select_related("resource_type")
    return {r.resource_type.name: r for r in resources}


@login_required
def planet_detail(request, planet_id):
    if is_game_master(request.user):
        messages.error(request, "Acceso denegado: las cuentas administrativas no tienen planetas asignados.")
        return redirect("gm_dashboard")
    planet = get_object_or_404(Planet, id=planet_id, owner__user=request.user)
    tick_planet_production(planet)
    my_planets = Planet.objects.filter(owner__user=request.user)
    res_dict = _ensure_planet_resources(planet)

    if request.method == "POST":
        if "rename_planet" in request.POST:
            new_name = request.POST.get("new_name", "").strip()
            if new_name:
                planet.name = new_name
                planet.save(update_fields=["name"])
            return redirect("planet_detail", planet_id=planet.id)

        if "build_building" in request.POST:
            building_type = get_object_or_404(BuildingType, id=request.POST.get("building_id"))
            upgrade_building(planet, building_type, res_dict)
            return redirect("planet_detail", planet_id=planet.id)

    buildings_info = get_buildings_info_for_planet(planet, res_dict)
    units = PlanetUnit.objects.filter(planet=planet).select_related("unit_type")
    available_units = UnitType.objects.all()

    context = {
        "planet": planet,
        "my_planets": my_planets,
        "resources": res_dict.values(),
        "buildings_info": buildings_info,
        "units": units,
        "available_units": available_units,
    }
    return render(request, "core/planet_detail.html", context)


@game_master_required
def gm_dashboard(request):
    """Main dashboard for game masters."""
    buildings = BuildingType.objects.all()
    units = UnitType.objects.all()
    settings = GameSettings.load()
    
    context = {
        "buildings": buildings,
        "units": units,
        "settings": settings,
        "can_create_superusers": request.user.is_superuser,
    }
    return render(request, "core/game_master/dashboard.html", context)


@game_master_required
def gm_create_user(request):
    if request.method == "POST":
        form = PrivilegedUserCreateForm(request.POST, creator_user=request.user)
        if form.is_valid():
            created_user = form.save()
            messages.success(request, f"Usuario '{created_user.username}' creado con éxito.")
            return redirect("gm_dashboard")
    else:
        form = PrivilegedUserCreateForm(creator_user=request.user)

    return render(
        request,
        "core/game_master/edit_entity.html",
        {
            "form": form,
            "title": "Crear usuario administrativo",
            "description": "Superusuario: puede crear superusuarios y Game Masters. Game Master: solo puede crear Game Masters.",
            "entity_name": "Usuario",
        },
    )


@game_master_required
def gm_edit_settings(request):
    settings = GameSettings.load()
    if request.method == "POST":
        form = GameSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully.")
            return redirect("gm_dashboard")
    else:
        form = GameSettingsForm(instance=settings)
        
    return render(request, "core/game_master/edit_entity.html", {
        "form": form,
        "title": "Edit Global Game Settings",
        "entity_name": "Game Settings"
    })

@game_master_required
def gm_edit_building(request, pk):
    building = get_object_or_404(BuildingType, pk=pk)
    if request.method == "POST":
        form = BuildingTypeForm(request.POST, instance=building)
        if form.is_valid():
            form.save()
            messages.success(request, f"Building '{building.name}' updated successfully.")
            return redirect("gm_dashboard")
    else:
        form = BuildingTypeForm(instance=building)
        
    return render(request, "core/game_master/edit_entity.html", {
        "form": form,
        "title": f"Edit Building: {building.name}",
        "entity_name": building.name
    })

@game_master_required
def gm_edit_unit(request, pk):
    unit = get_object_or_404(UnitType, pk=pk)
    if request.method == "POST":
        form = UnitTypeForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, f"Unit '{unit.name}' updated successfully.")
            return redirect("gm_dashboard")
    else:
        form = UnitTypeForm(instance=unit)
        
    return render(request, "core/game_master/edit_entity.html", {
        "form": form,
        "title": f"Edit Unit: {unit.name}",
        "entity_name": unit.name
    })
