import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_juego.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Dictator, Planet

def verify():
    # Clean up previous test
    if User.objects.filter(username='test_dictator').exists():
        User.objects.get(username='test_dictator').delete()
        print("Cleaned up missing previous test user.")

    print("Creating user 'test_dictator'...")
    user = User.objects.create_user(username='test_dictator', password='password123')
    
    try:
        dictator = Dictator.objects.get(user=user)
        print(f"Dictator profile created: {dictator}")
        
        if dictator.main_planet:
            print(f"SUCCESS: Assigned planet: {dictator.main_planet}")
            print(f"Planet owner: {dictator.main_planet.owner}")
            assert dictator.main_planet.owner == dictator
        else:
            print("FAILURE: No planet assigned.")
            
    except Dictator.DoesNotExist:
        print("FAILURE: Dictator profile not created.")
    except Exception as e:
        print(f"bwaka: {e}")

if __name__ == "__main__":
    verify()
