import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_juego.settings')
django.setup()

from core.models import BuildingType

def update_cost():
    try:
        bt = BuildingType.objects.get(name="Planta Eolica")
        # Define base cost appropriate for level 1
        # It's free at level 0->1, but we need a base cost for scaling 1->2+
        # Let's say base cost is 50 Plastilina and 30 Café
        bt.cost = {'Plastilina': 50, 'Café con Leche': 30}
        bt.save()
        print(f"Updated {bt.name} cost to {bt.cost}")
    except BuildingType.DoesNotExist:
        print("Planta Eolica not found")

if __name__ == "__main__":
    update_cost()
