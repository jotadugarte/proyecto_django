from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from core.models import (
    Galaxy,
    SolarSystem,
    Planet,
    ResourceType,
    BuildingType,
    UnitType,
    Dictator,
)


class Command(BaseCommand):
    help = "Setup initial game data (galaxy, systems, planets, resources, admin). Use --test to also create test users (orion, perseo)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--test",
            action="store_true",
            dest="test",
            help="Create test dictator users (orion, perseo). Omit for production (admin only).",
        )

    def handle(self, *args, **options) -> None:
        test_mode: bool = options["test"]
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
            ('Planta Eolica', 'extraction', {'Energía Eólica': 20}, {'Energía Eólica': 20}),  # Nivel 0->1 gratis; 1->2+ usa este coste base
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

        # 6. Admin superuser (for /admin/)
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write("Created superuser 'admin' (password: admin).")
        else:
            self.stdout.write("Superuser 'admin' already exists.")

        # 7. Test dictator users (only when --test)
        if test_mode:
            dictator_users = [
                ("orion", "orion1234"),
                ("perseo", "perseo1234"),
            ]
            for username, password in dictator_users:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, password=password)
                    dictator = Dictator.objects.get(user=user)
                    if dictator.main_planet:
                        self.stdout.write(f"Created dictator '{username}' -> planet {dictator.main_planet}.")
                    else:
                        self.stdout.write(self.style.WARNING(f"Created '{username}' but no free planet assigned."))
                else:
                    self.stdout.write(f"User '{username}' already exists.")
        else:
            self.stdout.write("Skipping test users (production mode). Use --test to create orion/perseo.")

        self.stdout.write(self.style.SUCCESS("Game Setup Complete!"))
