from django.core.management.base import BaseCommand
from core.models import Galaxy, SolarSystem, Planet, ResourceType, BuildingType, UnitType
import math

class Command(BaseCommand):
    help = 'Setup initial game data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Setting up game data...")

        # 1. Galaxy
        galaxy, created = Galaxy.objects.get_or_create(name="Andrómeda")
        if created:
            self.stdout.write("Created Galaxy 'Andrómeda'")
        
        # 2. Resources
        resources = ['Plastilina', 'Energía Eólica', 'Café con Leche']
        for r_name in resources:
            ResourceType.objects.get_or_create(name=r_name)
        self.stdout.write(f"Ensured {len(resources)} ResourceTypes")

        # 3. Buildings
        buildings = [
            # Extractores
            ('Mina de Plastilina', 'extraction', {'Energía Eólica': 10}, {'Plastilina': 10}),
            ('Planta Eolica', 'extraction', {}, {'Energía Eólica': 20}), # Costo 0 nivel 1
            ('Siembra de Café con Vaca', 'extraction', {'Plastilina': 100, 'Energía Eólica': 50}, {'Café con Leche': 5}),
            
            # Hangar
            ('Fábrica de naves', 'hangar', {'Plastilina': 500, 'Café con Leche': 100}, {}),
            
            # Defensas
            ('Parque de Agua', 'defense', {'Plastilina': 200}, {}),
            ('Pistola de Agua', 'defense', {'Plastilina': 150}, {}),
        ]
        for name, cat, cost, prod in buildings:
            BuildingType.objects.update_or_create(
                name=name,
                defaults={'category': cat, 'cost': cost, 'production': prod}
            )
        self.stdout.write(f"Ensured {len(buildings)} BuildingTypes")

        # 4. Units
        units = [
            ('Nave de Carga', 'ship', {'attack': 0, 'defense': 10, 'cargo': 100}, {'Plastilina': 200}),
            ('Caza', 'ship', {'attack': 50, 'defense': 20, 'cargo': 0}, {'Plastilina': 500, 'Energía Eólica': 100}),
            ('Sonda Mirona', 'ship', {'attack': 0, 'defense': 0, 'cargo': 0, 'spy': True}, {'Energía Eólica': 50}),
        ]
        for name, cat, stats, cost in units:
            UnitType.objects.get_or_create(
                name=name, 
                defaults={'category': cat, 'stats': stats, 'cost': cost}
            )
        self.stdout.write(f"Ensured {len(units)} UnitTypes")

        # 5. Universe Generation
        # 256 systems = 16x16 grid
        systems_count = 0
        planets_count = 0
        
        # Check if universe exists to avoid duplication/slowness on re-run
        if SolarSystem.objects.filter(galaxy=galaxy).count() < 256:
            self.stdout.write("Generating Universe (this might take a moment)...")
            
            # Use bulk_create for performance
            systems_to_create = []
            planets_to_create = []

            for x in range(16):
                for y in range(16):
                    # We can't use bulk_create for systems easily if we need their IDs for planets immediately
                    # unless we save them first.
                    # Or we just create them one by one, 256 is small.
                    pass

            # Transactional approach for speed
            from django.db import transaction
            
            with transaction.atomic():
                for x in range(16):
                    for y in range(16):
                        sys, created = SolarSystem.objects.get_or_create(galaxy=galaxy, x=x, y=y)
                        if created:
                            systems_count += 1
                            # Create 9 planets
                            for i in range(1, 10):
                                planets_to_create.append(Planet(
                                    system=sys,
                                    orbit_index=i,
                                    name=f"Planeta {sys.x}-{sys.y}-{i}"
                                ))
            
                if planets_to_create:
                    Planet.objects.bulk_create(planets_to_create)
                    planets_count = len(planets_to_create)

            self.stdout.write(f"Generated {systems_count} Solar Systems and {planets_count} Planets.")
        else:
            self.stdout.write("Universe already exists.")

        self.stdout.write(self.style.SUCCESS('Game Setup Complete!'))
