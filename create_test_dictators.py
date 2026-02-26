import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_juego.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Dictator

def create_dictator(username):
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists.")
        user = User.objects.get(username=username)
    else:
        print(f"Creating user '{username}'...")
        user = User.objects.create_user(username=username, password='password123')
    
    try:
        dictator = Dictator.objects.get(user=user)
        if dictator.main_planet:
            print(f"SUCCESS: '{username}' owns {dictator.main_planet}")
        else:
            print(f"FAILURE: '{username}' has NO planet!")
    except Dictator.DoesNotExist:
         print(f"FAILURE: '{username}' has NO dictator profile!")

if __name__ == "__main__":
    create_dictator('orion')
    create_dictator('perseo')
