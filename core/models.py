from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Galaxy(models.Model):
    name = models.CharField(max_length=100, default="Vía Láctea")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Galaxies"

class SolarSystem(models.Model):
    galaxy = models.ForeignKey(Galaxy, on_delete=models.CASCADE, related_name='systems')
    x = models.IntegerField(help_text="Coordenada X en la galaxia")
    y = models.IntegerField(help_text="Coordenada Y en la galaxia")
    # Validar que x, y estén dentro del rango si es necesario (ej. 0-15 para 256 sistemas en 16x16)

    @property
    def number(self):
        # Calculate linear number 1-256 based on 16x16 grid
        return (self.x * 16) + self.y + 1

    def __str__(self):
        return f"Sistema {self.number}"

    class Meta:
        unique_together = ('galaxy', 'x', 'y')

class ResourceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class BuildingType(models.Model):
    CATEGORY_CHOICES = [
        ('extraction', 'Extracción'),
        ('construction', 'Construcción'),
        ('defense', 'Defensa'),
        ('other', 'Otro'),
    ]
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True)
    cost = models.JSONField(default=dict, help_text="Costo base (ej: {'Plastilina': 100})")
    production = models.JSONField(default=dict, help_text="Producción base (ej: {'Energía': 10})")

    def __str__(self):
        return self.name

class UnitType(models.Model):
    CATEGORY_CHOICES = [
        ('ship', 'Nave'),
        ('defense', 'Defensa'),
    ]
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    stats = models.JSONField(default=dict, help_text="Estadísticas (Ataque, Defensa, Carga, etc.)")
    cost = models.JSONField(default=dict, help_text="Costo base")

    def __str__(self):
        return self.name

class Dictator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dictator_profile')
    main_planet = models.ForeignKey('Planet', on_delete=models.SET_NULL, null=True, blank=True, related_name='capital_of')

    def __str__(self):
        return self.user.username

class Planet(models.Model):
    system = models.ForeignKey(SolarSystem, on_delete=models.CASCADE, related_name='planets')
    orbit_index = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(Dictator, on_delete=models.SET_NULL, null=True, blank=True, related_name='planets')
    
    # Recursos actuales almacenados en el planeta
    resources = models.ManyToManyField(ResourceType, through='PlanetResource')
    buildings = models.ManyToManyField(BuildingType, through='PlanetBuilding')
    units = models.ManyToManyField(UnitType, through='PlanetUnit')

    class Meta:
        unique_together = ('system', 'orbit_index')
        ordering = ['system', 'orbit_index']

    def __str__(self):
        return f"{self.name} [{self.orbit_index}:{self.system.number}]"

# Tablas intermedias para almacenar cantidades/niveles

class PlanetResource(models.Model):
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    amount = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ('planet', 'resource_type')

class PlanetBuilding(models.Model):
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)

    class Meta:
        unique_together = ('planet', 'building_type')

class PlanetUnit(models.Model):
    planet = models.ForeignKey(Planet, on_delete=models.CASCADE)
    unit_type = models.ForeignKey(UnitType, on_delete=models.CASCADE)
    quantity = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ('planet', 'unit_type')
