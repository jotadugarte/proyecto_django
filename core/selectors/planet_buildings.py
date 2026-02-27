"""Selector: build buildings info (levels, costs, production display) for planet detail."""

from core.models import BuildingType, Planet, PlanetBuilding, PlanetResource


def get_buildings_info_for_planet(
    planet: Planet,
    res_dict: dict[str, PlanetResource],
) -> list[dict]:
    """
    Return a list of building info dicts for the planet detail view.

    Each dict has: type, current_level, next_level, cost_display, can_build, production_display.
    res_dict: mapping resource type name -> PlanetResource (for can_build checks).
    """
    buildings_built = PlanetBuilding.objects.filter(planet=planet).select_related("building_type")
    built_dict = {b.building_type.id: b.level for b in buildings_built}

    result: list[dict] = []
    for b_type in BuildingType.objects.all():
        current_level = built_dict.get(b_type.id, 0)
        next_level = current_level + 1

        cost_display: dict[str, int] = {}
        can_build = True
        if b_type.name == "Planta Eolica" and current_level == 0:
            pass
        else:
            for res_name, amount in b_type.cost.items():
                c = int(amount * (1.5 ** current_level)) if current_level > 0 else amount
                cost_display[res_name] = c
                if res_name not in res_dict or res_dict[res_name].amount < c:
                    can_build = False

        production_display: list[dict] = []
        if b_type.category == "extraction" and (b_type.production or {}):
            for res_name, base_rate in b_type.production.items():
                try:
                    rate_per_hour = float(base_rate) * max(0, current_level)
                except (TypeError, ValueError):
                    rate_per_hour = 0.0
                production_display.append({
                    "resource_name": res_name,
                    "per_hour": rate_per_hour,
                    "per_minute": rate_per_hour / 60.0 if rate_per_hour else 0.0,
                })

        result.append({
            "type": b_type,
            "current_level": current_level,
            "next_level": next_level,
            "cost_display": cost_display,
            "can_build": can_build,
            "production_display": production_display,
        })
    return result
