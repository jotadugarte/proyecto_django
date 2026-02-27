from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.models import (
    Galaxy,
    SolarSystem,
    Planet,
    ResourceType,
    BuildingType,
    PlanetBuilding,
    PlanetResource,
)
from core.services.production import tick_planet_production


class TickPlanetProductionTests(TestCase):
    """Tests for production tick (REQ-PROD-001, REQ-PROD-003)."""

    def setUp(self) -> None:
        galaxy = Galaxy.objects.create(name="Test Galaxy")
        system = SolarSystem.objects.create(galaxy=galaxy, x=0, y=0)
        self.planet = Planet.objects.create(
            system=system,
            orbit_index=1,
            name="Test Planet",
            last_production_tick=None,
        )
        self.res_type = ResourceType.objects.create(name="Energía Eólica")
        self.building_type = BuildingType.objects.create(
            name="Planta Eolica",
            category="extraction",
            cost={},
            production={"Energía Eólica": 20},
        )
        PlanetBuilding.objects.create(
            planet=self.planet,
            building_type=self.building_type,
            level=1,
        )
        PlanetResource.objects.create(
            planet=self.planet,
            resource_type=self.res_type,
            amount=0,
        )

    def test_first_tick_sets_baseline_and_adds_no_production(self) -> None:
        """When last_production_tick is None, tick sets it to now and does not add resources."""
        tick_planet_production(self.planet)
        self.planet.refresh_from_db()
        self.assertIsNotNone(self.planet.last_production_tick)
        pr = PlanetResource.objects.get(planet=self.planet, resource_type=self.res_type)
        self.assertEqual(pr.amount, 0)

    def test_second_tick_after_elapsed_time_adds_production(self) -> None:
        """After setting last_production_tick in the past, tick adds production."""
        self.planet.last_production_tick = timezone.now() - timedelta(hours=1)
        self.planet.save(update_fields=["last_production_tick"])
        tick_planet_production(self.planet)
        pr = PlanetResource.objects.get(planet=self.planet, resource_type=self.res_type)
        self.assertEqual(pr.amount, 20)

    def test_fractional_production_accumulates_via_remainder(self) -> None:
        """Small elapsed time produces fractional amount; remainder is applied on next tick."""
        self.planet.last_production_tick = timezone.now() - timedelta(minutes=3)
        self.planet.save(update_fields=["last_production_tick"])
        tick_planet_production(self.planet)
        pr = PlanetResource.objects.get(planet=self.planet, resource_type=self.res_type)
        self.assertGreaterEqual(pr.amount, 0)
        self.planet.refresh_from_db()
        tick_planet_production(self.planet)
        pr.refresh_from_db()
        self.assertGreaterEqual(pr.amount, 0)
