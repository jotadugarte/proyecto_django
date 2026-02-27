"""Service: building construction and upgrade logic."""

from django.db import transaction

from core.models import BuildingType, Planet, PlanetBuilding, PlanetResource


def _calculate_build_cost(building_type: BuildingType, current_level: int) -> dict[str, int]:
    """Return the resource cost to upgrade a building to the next level.

    Returns an empty dict if the building is free (e.g. Planta Eolica level 0→1).
    """
    is_free = building_type.name == "Planta Eolica" and current_level == 0
    if is_free:
        return {}

    return {
        res_name: int(amount * (1.5 ** current_level)) if current_level > 0 else int(amount)
        for res_name, amount in building_type.cost.items()
    }


def can_afford(cost: dict[str, int], res_dict: dict[str, PlanetResource]) -> bool:
    """Return True if the planet has enough resources to pay `cost`."""
    return all(
        res_name in res_dict and res_dict[res_name].amount >= amount
        for res_name, amount in cost.items()
    )


@transaction.atomic
def upgrade_building(
    planet: Planet,
    building_type: BuildingType,
    res_dict: dict[str, PlanetResource],
) -> bool:
    """Attempt to upgrade `building_type` on `planet`.

    Deducts resources and increments the building level atomically.
    Returns True on success, False if the planet cannot afford the upgrade.
    """
    pb, _ = PlanetBuilding.objects.get_or_create(planet=planet, building_type=building_type)
    cost = _calculate_build_cost(building_type, pb.level)

    if not can_afford(cost, res_dict):
        return False

    # Deduct resources in bulk
    updated_resources: list[PlanetResource] = []
    for res_name, amount in cost.items():
        resource = res_dict[res_name]
        resource.amount -= amount
        updated_resources.append(resource)

    PlanetResource.objects.bulk_update(updated_resources, ["amount"])

    pb.level += 1
    pb.save(update_fields=["level"])
    return True
