# Data migration: set base cost for Planta Eolica (level 0->1 stays free in view logic)

from django.db import migrations


def set_planta_eolica_cost(apps, schema_editor):
    BuildingType = apps.get_model("core", "BuildingType")
    BuildingType.objects.filter(name="Planta Eolica", cost={}).update(
        cost={"Energía Eólica": 20}
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(set_planta_eolica_cost, noop),
    ]
