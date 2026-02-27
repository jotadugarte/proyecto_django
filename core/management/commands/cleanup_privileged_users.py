from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from core.models import Dictator, Planet


class Command(BaseCommand):
    help = "Removes dictator profiles and planet ownership for privileged users (is_staff or is_superuser)."

    def handle(self, *args, **options):
        privileged_users = User.objects.filter(is_active=True).filter(is_staff=True) | User.objects.filter(
            is_active=True, is_superuser=True
        )
        privileged_user_ids = list(privileged_users.values_list("id", flat=True))

        dictators = Dictator.objects.filter(user_id__in=privileged_user_ids)
        dictator_ids = list(dictators.values_list("id", flat=True))

        planets_updated = Planet.objects.filter(owner_id__in=dictator_ids).update(owner=None)
        dictators.update(main_planet=None)
        deleted_count, _ = dictators.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Cleanup complete. Unassigned planets: {planets_updated}. Deleted dictator profiles: {deleted_count}."
            )
        )
