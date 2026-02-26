import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_juego.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Planet, BuildingType, PlanetBuilding, Dictator

def reset_wind_plant():
    try:
        user = User.objects.get(username='orion')
        dictator = Dictator.objects.get(user=user)
        planet = Planet.objects.filter(owner=dictator).first()
        
        if not planet:
            print(f"User {user.username} (Dictator) has no planet.")
            return

        building_type = BuildingType.objects.get(name="Planta Eolica")
        
        pb, created = PlanetBuilding.objects.get_or_create(planet=planet, building_type=building_type)
        pb.level = 0
        pb.save()
        
        print(f"Successfully reset '{building_type.name}' to Level 0 for user '{user.username}' on planet '{planet.name}'.")

    except User.DoesNotExist:
        print("User 'orion' not found.")
    except BuildingType.DoesNotExist:
        print("Building 'Planta Eolica' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    reset_wind_plant()
