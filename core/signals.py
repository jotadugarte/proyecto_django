import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Dictator, Planet

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_dictator_profile(sender, instance, created, **kwargs) -> None:
    """On new User creation: create Dictator and assign one unoccupied planet."""
    if not created:
        return
    if instance.is_staff or instance.is_superuser:
        logger.info("Skipping dictator/planet assignment for privileged user %s", instance.username)
        return
    dictator = Dictator.objects.create(user=instance)
    free_planet = Planet.objects.filter(owner__isnull=True).order_by("?").first()
    if free_planet:
        free_planet.owner = dictator
        free_planet.save(update_fields=["owner"])
        dictator.main_planet = free_planet
        dictator.save(update_fields=["main_planet"])
        logger.info("Assigned planet %s to user %s", free_planet, instance.username)
    else:
        logger.warning("No free planets available for user %s", instance.username)
