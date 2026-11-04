"""Create a new $500 test request for two existing demo users, never reset data."""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import User
from services.models import ServiceRequest, Quote


class Command(BaseCommand):
    help = 'Crea una solicitud independiente de $500 para probar pagos sin dinero real.'

    def add_arguments(self, parser):
        parser.add_argument('--client', required=True, help='Email del cliente de demostración')
        parser.add_argument('--provider', required=True, help='Email del prestador de demostración')

    @transaction.atomic
    def handle(self, *args, **options):
        if not (settings.DEBUG and settings.PAYMENTS_DEMO_ENABLED):
            raise CommandError('Este comando solo funciona en modo de demostración local.')
        client = User.objects.filter(email=options['client'], role='CLIENT', is_active=True).first()
        provider = User.objects.filter(email=options['provider'], role='PROVIDER', is_active=True).first()
        profile = getattr(provider, 'provider_profile', None)
        if not client or not profile or not profile.is_active:
            raise CommandError('Se necesitan un cliente y un perfil de prestador activos ya creados.')
        category, commune = profile.categories.first(), profile.communes.first()
        if not category or not commune:
            raise CommandError('El prestador debe tener una categoría y comuna configuradas.')
        sr = ServiceRequest.objects.create(client=client, provider=provider, category=category,
            commune=commune, status='ACCEPTED', address='Domicilio ficticio para demostración',
            description='Prueba de pago de $500 · no contrata un trabajo real')
        Quote.objects.create(service_request=sr, provider=provider, status='ACCEPTED',
            description='Servicio ficticio para comprobar Webpay y el chat', price=500)
        self.stdout.write(self.style.SUCCESS(f'Solicitud #{sr.pk} creada: total $500 CLP de prueba; dinero real $0.'))
