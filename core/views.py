from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_http_methods

from .forms import UserRegistrationForm
from .models import Planet, BuildingType, PlanetBuilding, PlanetResource, PlanetUnit, ResourceType, UnitType
from .services.production import tick_planet_production


class CustomLoginView(LoginView):
    """Login view that shows a user-facing message on invalid credentials."""

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña inválido.")
        return super().form_invalid(form)


@require_http_methods(["GET", "POST"])
def register(request):
    """Register a new user (username, name, password). Redirects to login on success."""
    if request.user.is_authenticated:
        return redirect("/")
    form = UserRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from django.contrib.auth.models import User

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
    # Redirect to the main planet of the user
    try:
        dictator = request.user.dictator_profile
        if dictator.main_planet:
            return redirect('planet_detail', planet_id=dictator.main_planet.id)
    except:
        pass
    return render(request, 'core/no_planet.html')

@login_required
def planet_detail(request, planet_id):
    planet = get_object_or_404(Planet, id=planet_id, owner__user=request.user)

    tick_planet_production(planet)

    # Get all planets for navigation
    my_planets = Planet.objects.filter(owner__user=request.user)

    # Resources
    for rt in ResourceType.objects.all():
        PlanetResource.objects.get_or_create(planet=planet, resource_type=rt)
    resources = PlanetResource.objects.filter(planet=planet)
    res_dict = {r.resource_type.name: r for r in resources}

    # Handle Actions (Build/Upgrade)
    if request.method == 'POST':
        if 'rename_planet' in request.POST:
            new_name = request.POST.get('new_name')
            if new_name:
                planet.name = new_name
                planet.save()
                return redirect('planet_detail', planet_id=planet.id)
        
        elif 'build_building' in request.POST:
            building_id = request.POST.get('building_id')
            building_type = get_object_or_404(BuildingType, id=building_id)
            
            # Get current level
            pb, created = PlanetBuilding.objects.get_or_create(planet=planet, building_type=building_type)
            current_level = pb.level
            
            # Calculate Cost
            cost = {}
            # Special case for Planta Eolica level 0 -> 1 is 0 cost
            if building_type.name == "Planta Eolica" and current_level == 0:
                pass # Cost remains empty
            else:
                for res_name, amount in building_type.cost.items():
                    c = int(amount * (1.5 ** current_level)) if current_level > 0 else amount
                    cost[res_name] = c
            
            # Check correctness
            can_afford = True
            for res_name, amount in cost.items():
                if res_name not in res_dict or res_dict[res_name].amount < amount:
                    can_afford = False
                    break
            
            if can_afford:
                # Deduct resources
                for res_name, amount in cost.items():
                    res_dict[res_name].amount -= amount
                    res_dict[res_name].save()
                
                # Upgrade
                pb.level += 1
                pb.save()
                return redirect('planet_detail', planet_id=planet.id)

    # Buildings & Logic
    buildings_built = PlanetBuilding.objects.filter(planet=planet).select_related('building_type')
    built_dict = {b.building_type.id: b.level for b in buildings_built}
    
    available_buildings = []
    all_building_types = BuildingType.objects.all()
    
    for b_type in all_building_types:
        current_level = built_dict.get(b_type.id, 0)
        next_level = current_level + 1
        
        # Calculate cost for next level
        cost_display = {}
        can_build = True
        
        # Special case for Planta Eolica level 0 -> 1 is 0 cost
        if b_type.name == "Planta Eolica" and current_level == 0:
             pass # cost_display remains empty -> "Gratis"
        else:
            for res_name, amount in b_type.cost.items():
                c = int(amount * (1.5 ** current_level)) if current_level > 0 else amount
                cost_display[res_name] = c
                
                # Validation
                if res_name not in res_dict or res_dict[res_name].amount < c:
                    can_build = False

        production_display = []
        if b_type.category == "extraction" and (b_type.production or {}):
            for res_name, base_rate in b_type.production.items():
                try:
                    rate_per_hour = float(base_rate) * max(0, current_level)
                except (TypeError, ValueError):
                    rate_per_hour = 0
                production_display.append({
                    "resource_name": res_name,
                    "per_hour": rate_per_hour,
                    "per_minute": rate_per_hour / 60.0 if rate_per_hour else 0,
                })

        available_buildings.append({
            "type": b_type,
            "current_level": current_level,
            "next_level": next_level,
            "cost_display": cost_display,
            "can_build": can_build,
            "production_display": production_display,
        })

    # Units
    units = PlanetUnit.objects.filter(planet=planet).select_related('unit_type')
    available_units = UnitType.objects.all()

    context = {
        'planet': planet,
        'my_planets': my_planets,
        'resources': resources,
        'buildings_info': available_buildings, # List of dicts with level info
        'units': units,
        'available_units': available_units,
    }
    return render(request, 'core/planet_detail.html', context)
