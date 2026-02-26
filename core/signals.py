from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Dictator, Planet

@receiver(post_save, sender=User)
def create_dictator_profile(sender, instance, created, **kwargs):
    if created:
        # Create Dictator profile
        dictator = Dictator.objects.create(user=instance)
        
        # Assign a random planet
        # We try to find a planet without owner
        free_planet = Planet.objects.filter(owner__isnull=True).order_by('?').first()
        
        if free_planet:
            free_planet.owner = dictator
            free_planet.save()
            
            dictator.main_planet = free_planet
            dictator.save()
            print(f"Assigned planet {free_planet} to user {instance.username}")
        else:
            print(f"WARNING: No free planets available for user {instance.username}")
