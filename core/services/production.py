"""Production tick: accumulate resources over time from extractor building levels."""

from datetime import datetime

from django.utils import timezone

from core.models import Planet, PlanetBuilding, PlanetResource, ResourceType


def _compute_produced(planet: Planet, now: datetime) -> dict[str, float] | None:
    """
    Compute production amounts since last_production_tick. Returns None if no production to apply.
    If last_production_tick is None, sets it to now and returns None.
    """
    if planet.last_production_tick is None:
        planet.last_production_tick = now
        planet.save(update_fields=["last_production_tick"])
        return None

    elapsed_seconds = (now - planet.last_production_tick).total_seconds()
    
    # Import here to avoid circular dependencies if any, though models could be imported at top level
    from core.models import GameSettings
    settings = GameSettings.load()
    
    elapsed_hours = (elapsed_seconds / 3600.0) * settings.production_speed_multiplier
    
    if elapsed_hours <= 0:
        return None

    produced: dict[str, float] = {}
    extractors = PlanetBuilding.objects.filter(
        planet=planet,
        building_type__category="extraction",
        level__gte=1,
    ).select_related("building_type")

    for pb in extractors:
        level = pb.level
        for res_name, base_rate in (pb.building_type.production or {}).items():
            try:
                rate = float(base_rate) * level
            except (TypeError, ValueError):
                continue
            produced[res_name] = produced.get(res_name, 0.0) + rate * elapsed_hours

    return produced


def _apply_production_to_planet(
    planet: Planet,
    produced: dict[str, float],
    now: datetime,
) -> None:
    """Update planet resources and remainder from produced amounts; set last_production_tick."""
    remainder = getattr(planet, "production_remainder", None) or {}
    new_remainder: dict[str, float] = dict(remainder)

    for res_name, amount in produced.items():
        total = amount + remainder.get(res_name, 0.0)
        if total <= 0:
            continue
        try:
            res_type = ResourceType.objects.get(name=res_name)
        except ResourceType.DoesNotExist:
            continue
        integer_part = int(total)
        fractional = total - integer_part
        if fractional >= 1e-9:
            new_remainder[res_name] = fractional
        else:
            new_remainder.pop(res_name, None)
        pr, _ = PlanetResource.objects.get_or_create(
            planet=planet,
            resource_type=res_type,
            defaults={"amount": 0},
        )
        pr.amount += integer_part
        pr.save(update_fields=["amount"])

    planet.last_production_tick = now
    planet.production_remainder = new_remainder
    planet.save(update_fields=["last_production_tick", "production_remainder"])


def tick_planet_production(planet: Planet) -> None:
    """
    Apply extractor production since last_production_tick; update planet resources and tick time.

    Only buildings with category 'extraction' and level >= 1 produce. Production is
    base rate (per hour at level 1) * level * elapsed hours.
    """
    assert planet.pk is not None, "Planet must be persisted to run production tick"
    now = timezone.now()
    produced = _compute_produced(planet, now)
    if produced is not None:
        _apply_production_to_planet(planet, produced, now)
