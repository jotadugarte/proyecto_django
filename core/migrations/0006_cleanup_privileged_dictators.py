from django.db import migrations


def cleanup_privileged_dictators(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Dictator = apps.get_model("core", "Dictator")
    Planet = apps.get_model("core", "Planet")

    privileged_users = User.objects.filter(is_active=True).filter(is_staff=True) | User.objects.filter(
        is_active=True, is_superuser=True
    )
    privileged_user_ids = list(privileged_users.values_list("id", flat=True))

    dictators = Dictator.objects.filter(user_id__in=privileged_user_ids)

    # Unassign planets owned by these dictators
    Planet.objects.filter(owner_id__in=dictators.values_list("id", flat=True)).update(owner=None)

    # Clear main planet pointers
    dictators.update(main_planet=None)

    # Delete dictator profiles for privileged users
    dictators.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_gamesettings"),
    ]

    operations = [
        migrations.RunPython(cleanup_privileged_dictators, migrations.RunPython.noop),
    ]
