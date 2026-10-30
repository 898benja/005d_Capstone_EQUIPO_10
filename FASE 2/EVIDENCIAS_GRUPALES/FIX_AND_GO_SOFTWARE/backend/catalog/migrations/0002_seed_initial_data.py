"""Datos iniciales: categorías de servicio y comunas de Santiago."""

from django.db import migrations


CATEGORIES = [
    {'name': 'Agua / Gasfitería', 'slug': 'agua-gasfiteria', 'description': 'Reparaciones y mantención de cañerías, grifos, calefones y sistemas de agua.', 'icon': 'water'},
    {'name': 'Electricidad', 'slug': 'electricidad', 'description': 'Instalaciones eléctricas, reparación de enchufes, tableros y luminarias.', 'icon': 'bolt'},
    {'name': 'Gas', 'slug': 'gas', 'description': 'Instalación, revisión y mantención de artefactos y redes de gas.', 'icon': 'flame'},
]

COMMUNES = [
    {'name': 'Cerrillos', 'slug': 'cerrillos'},
    {'name': 'Estación Central', 'slug': 'estacion-central'},
    {'name': 'Lo Prado', 'slug': 'lo-prado'},
    {'name': 'Maipú', 'slug': 'maipu'},
    {'name': 'Pudahuel', 'slug': 'pudahuel'},
    {'name': 'Quinta Normal', 'slug': 'quinta-normal'},
    {'name': 'Santiago', 'slug': 'santiago'},
]


def seed_data(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    Commune = apps.get_model('catalog', 'Commune')
    for cat in CATEGORIES:
        Category.objects.get_or_create(slug=cat['slug'], defaults=cat)
    for com in COMMUNES:
        Commune.objects.get_or_create(slug=com['slug'], defaults=com)


def reverse_seed(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    Commune = apps.get_model('catalog', 'Commune')
    slugs_cat = [c['slug'] for c in CATEGORIES]
    slugs_com = [c['slug'] for c in COMMUNES]
    Category.objects.filter(slug__in=slugs_cat).delete()
    Commune.objects.filter(slug__in=slugs_com).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
