"""Perfiles sintéticos independientes: no modifica ubicaciones de usuarios reales."""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import User, ProviderProfile
from catalog.models import Category, Commune


class Command(BaseCommand):
    help = 'Crea tres prestadores ficticios con puntos públicos de demostración (solo DEBUG).'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not settings.DEBUG:
            raise CommandError('Solo disponible en desarrollo con DEBUG=true.')
        category = Category.objects.first()
        if not category:
            raise CommandError('Aplica primero las migraciones del catálogo.')
        for i, (lat, lon) in enumerate([(-33.4489,-70.6693),(-33.46,-70.65),(-33.49,-70.70)],1):
            user,created = User.objects.get_or_create(username=f'mapa_demo_{i}',defaults={
                'email':f'mapa_demo_{i}@example.test','role':'PROVIDER','first_name':f'Demo {i}',
            })
            if not created:
                continue  # No reescribir ni republicar decisiones de perfiles existentes.
            user.set_unusable_password();user.save(update_fields=['password'])
            p=ProviderProfile.objects.create(user=user,display_name=f'Prestador DEMO {i}',
                description='Perfil ficticio para demostrar el mapa. No contratar servicios reales.',
                latitude=lat,longitude=lon,map_visible=True)
            p.categories.add(category);p.communes.set(Commune.objects.all())
        self.stdout.write(self.style.SUCCESS('Perfiles de mapa DEMO disponibles.'))
