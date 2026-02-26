import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_juego.settings')
django.setup()

from core.models import BuildingType

def check_data():
    try:
        bt = BuildingType.objects.get(name="Planta Eolica")
        print(f"Building: {bt.name}")
        print(f"Cost: {bt.cost}")
        print(f"Category: {bt.category}")
    except BuildingType.DoesNotExist:
        print("Planta Eolica not found")

if __name__ == "__main__":
    check_data()
