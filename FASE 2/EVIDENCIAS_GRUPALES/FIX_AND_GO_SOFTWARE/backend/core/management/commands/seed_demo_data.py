"""Comando para poblar la base de datos con datos de demostración (BE-15).

Uso:
    python manage.py seed_demo_data          # Crear datos de demo
    python manage.py seed_demo_data --reset  # Limpiar y recrear desde cero

El comando es idempotente: puede ejecutarse varias veces sin duplicar registros.
Usa get_or_create para todas las entidades.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User, ProviderProfile
from catalog.models import Category, Commune
from services.models import ServiceRequest, Quote, Rating
from billing.models import MaterialExtra, PaymentOrder, ServiceMessage, ServiceDispute
from services.models import WorkEvidence
from django.db.models import Q


# ---------------------------------------------------------------------------
# Datos fijos de demo
# ---------------------------------------------------------------------------

CATEGORIES = [
    {'name': 'Agua y Gasfitería', 'slug': 'agua-gasfiteria',
     'description': 'Reparación de cañerías, grifería, destapes y filtraciones.',
     'icon': 'water'},
    {'name': 'Electricidad', 'slug': 'electricidad',
     'description': 'Instalaciones, tableros, enchufes y certificaciones SEC.',
     'icon': 'flash'},
    {'name': 'Gas', 'slug': 'gas',
     'description': 'Instalación y mantención de redes y artefactos a gas.',
     'icon': 'flame'},
    {'name': 'Cerrajería', 'slug': 'cerrajeria',
     'description': 'Apertura, cambio de chapas, cerraduras y copias de llaves.',
     'icon': 'key'},
    {'name': 'Pintura', 'slug': 'pintura',
     'description': 'Pintura interior, exterior y reparación de muros.',
     'icon': 'brush'},
]

COMMUNES = [
    {'name': 'Santiago', 'slug': 'santiago'},
    {'name': 'Maipú', 'slug': 'maipu'},
    {'name': 'Pudahuel', 'slug': 'pudahuel'},
    {'name': 'Estación Central', 'slug': 'estacion-central'},
    {'name': 'Providencia', 'slug': 'providencia'},
    {'name': 'Las Condes', 'slug': 'las-condes'},
    {'name': 'La Florida', 'slug': 'la-florida'},
    {'name': 'Ñuñoa', 'slug': 'nunoa'},
]

DEMO_PASSWORD = 'Demo2026!safe'
DEMO_USERNAMES = [
    'admin',
    'cliente',
    'cliente2',
    'prestador',
    'carla_electricista',
    'pedro_gasista',
    'ana_cerrajera',
]


class Command(BaseCommand):
    help = 'Crea datos de demostración para FIX&GO (idempotente)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Eliminar todos los datos de demo antes de recrear.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        self._create_categories()
        self._create_communes()
        admin = self._create_admin()
        cliente1 = self._create_client(
            'cliente', 'cliente@fixandgo.cl', 'Juan', 'Pérez',
        )
        cliente2 = self._create_client(
            'cliente2', 'maria@fixandgo.cl', 'María', 'González',
        )
        prov1 = self._create_provider(
            username='prestador',
            email='prestador@fixandgo.cl',
            first_name='Mario', last_name='Casas',
            display_name='Mario Casas - Gasfitería Experta',
            description='Especialista en filtraciones, cambio de grifería y destapes con más de 8 años de trayectoria.',
            years_experience=8,
            phone='+56 9 8765 4321',
            category_slugs=['agua-gasfiteria'],
            commune_slugs=['santiago', 'maipu', 'estacion-central'],
        )
        prov2 = self._create_provider(
            username='carla_electricista',
            email='carla@fixandgo.cl',
            first_name='Carla', last_name='Volta',
            display_name='Carla Volta - Soluciones Eléctricas',
            description='Instalaciones, tableros eléctricos, aumento de capacidad y certificación SEC clase B.',
            years_experience=5,
            phone='+56 9 1234 5678',
            category_slugs=['electricidad'],
            commune_slugs=['santiago', 'pudahuel'],
        )
        prov3 = self._create_provider(
            username='pedro_gasista',
            email='pedro@fixandgo.cl',
            first_name='Pedro', last_name='Fuentes',
            display_name='Pedro Fuentes - Gasista Certificado',
            description='Certificación SEC clase C. Instalación y mantención de redes y artefactos a gas.',
            years_experience=12,
            phone='+56 9 5555 1234',
            category_slugs=['gas', 'agua-gasfiteria'],
            commune_slugs=['santiago', 'providencia', 'nunoa', 'la-florida'],
        )
        prov4 = self._create_provider(
            username='ana_cerrajera',
            email='ana@fixandgo.cl',
            first_name='Ana', last_name='Llaves',
            display_name='Ana Llaves - Cerrajería 24h',
            description='Apertura de puertas, cambio de chapas, cerraduras de seguridad y copias.',
            years_experience=3,
            phone='+56 9 7777 8888',
            category_slugs=['cerrajeria'],
            commune_slugs=['santiago', 'maipu', 'providencia', 'las-condes'],
        )

        # Solicitudes en distintos estados
        self._create_demo_requests(cliente1, cliente2, prov1, prov2, prov3, prov4)

        self.stdout.write(self.style.SUCCESS(
            '\n¡Datos de demostración cargados exitosamente!\n\n'
            'Credenciales de acceso:\n'
            f'  Admin:     admin@fixandgo.cl / {DEMO_PASSWORD}\n'
            f'  Cliente 1: cliente@fixandgo.cl / {DEMO_PASSWORD}\n'
            f'  Cliente 2: maria@fixandgo.cl / {DEMO_PASSWORD}\n'
            f'  Prestador: prestador@fixandgo.cl / {DEMO_PASSWORD}\n'
            f'  Prestador: carla@fixandgo.cl / {DEMO_PASSWORD}\n'
            f'  Prestador: pedro@fixandgo.cl / {DEMO_PASSWORD}\n'
            f'  Prestador: ana@fixandgo.cl / {DEMO_PASSWORD}\n'
        ))

    # -----------------------------------------------------------------------
    # Creación de entidades
    # -----------------------------------------------------------------------

    def _create_categories(self):
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data,
            )
            if created:
                self.stdout.write(f'  + Categoría: {cat.name}')

    def _create_communes(self):
        for com_data in COMMUNES:
            com, created = Commune.objects.get_or_create(
                slug=com_data['slug'],
                defaults=com_data,
            )
            if created:
                self.stdout.write(f'  + Comuna: {com.name}')

    def _create_admin(self):
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@fixandgo.cl',
                'first_name': 'Administrador',
                'last_name': 'FIX&GO',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if created:
            admin.set_password(DEMO_PASSWORD)
            admin.save()
        if created:
            self.stdout.write(self.style.SUCCESS('  + Superuser admin creado'))
        return admin

    def _create_client(self, username, email, first_name, last_name):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': User.Role.CLIENT,
            },
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f'  + Cliente: {first_name} {last_name}'))
        return user

    def _create_provider(self, username, email, first_name, last_name,
                         display_name, description, years_experience,
                         phone, category_slugs, commune_slugs):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': User.Role.PROVIDER,
            },
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()

        profile, _ = ProviderProfile.objects.get_or_create(
            user=user,
            defaults={
                'display_name': display_name,
                'description': description,
                'years_experience': years_experience,
                'phone': phone,
                'is_active': True,
                'is_verified': True,
            },
        )
        for slug in category_slugs:
            cat = Category.objects.filter(slug=slug).first()
            if cat:
                profile.categories.add(cat)
        for slug in commune_slugs:
            com = Commune.objects.filter(slug=slug).first()
            if com:
                profile.communes.add(com)

        if created:
            self.stdout.write(self.style.SUCCESS(f'  + Prestador: {display_name}'))
        return user

    def _create_demo_requests(self, cliente1, cliente2, prov1, prov2, prov3, prov4):
        """Crear solicitudes de demo en varios estados."""
        cat_agua = Category.objects.filter(slug='agua-gasfiteria').first()
        cat_elec = Category.objects.filter(slug='electricidad').first()
        cat_gas = Category.objects.filter(slug='gas').first()
        cat_cerr = Category.objects.filter(slug='cerrajeria').first()
        com_stgo = Commune.objects.filter(slug='santiago').first()
        com_maipu = Commune.objects.filter(slug='maipu').first()
        com_provi = Commune.objects.filter(slug='providencia').first()

        if not all([cat_agua, cat_elec, com_stgo]):
            self.stdout.write(self.style.WARNING(
                '  ! No se encontraron categorías/comunas para crear solicitudes.'
            ))
            return

        # 1. Solicitud QUOTED — lista para aceptar en la demo
        sr1, created1 = ServiceRequest.objects.get_or_create(
            client=cliente1,
            provider=prov1,
            category=cat_agua,
            commune=com_stgo,
            description='Filtración en lavaplatos bajo el mueble de cocina. '
                        'Gotea de forma constante al abrir la llave de agua caliente.',
            defaults={
                'address': 'Av. Libertador Bernardo O\'Higgins 1234, Depto 402',
                'preferred_time': 'Tarde (15:00 a 18:00)',
                'status': ServiceRequest.Status.QUOTED,
            },
        )
        if created1:
            Quote.objects.get_or_create(
                service_request=sr1,
                provider=prov1,
                defaults={
                    'description': 'Revisión y cambio de sifón y flexible de agua caliente '
                                   'con repuestos estándar incluidos.',
                    'price': 35000,
                    'estimated_duration': '1 a 2 horas',
                    'notes': 'Incluye garantía de 30 días sobre el trabajo ejecutado.',
                    'status': Quote.Status.SUBMITTED,
                },
            )
            self.stdout.write('  + Solicitud #%d — QUOTED (lista para aceptar)' % sr1.pk)

        # 2. Solicitud PENDING — esperando cotización
        sr2, created2 = ServiceRequest.objects.get_or_create(
            client=cliente1,
            provider=prov2,
            category=cat_elec,
            commune=com_stgo,
            description='Apagones intermitentes en el segundo piso. Los interruptores '
                        'saltan sin motivo aparente.',
            defaults={
                'address': 'Pasaje Los Aromos 567, casa 12',
                'preferred_time': 'Mañana (09:00 a 12:00)',
                'status': ServiceRequest.Status.PENDING,
            },
        )
        if created2:
            self.stdout.write('  + Solicitud #%d — PENDING (esperando cotización)' % sr2.pk)

        # 3. Solicitud COMPLETED con valoración
        sr3, created3 = ServiceRequest.objects.get_or_create(
            client=cliente2,
            provider=prov1,
            category=cat_agua,
            commune=com_maipu,
            description='Llave de baño no cierra completamente y gotea toda la noche.',
            defaults={
                'address': 'Calle Los Olivos 890, Maipú',
                'preferred_time': 'Tarde',
                'status': ServiceRequest.Status.COMPLETED,
            },
        )
        if created3:
            Quote.objects.get_or_create(
                service_request=sr3,
                provider=prov1,
                defaults={
                    'description': 'Cambio de aireador y empaquetaduras de la grifería.',
                    'price': 25000,
                    'estimated_duration': '45 minutos',
                    'status': Quote.Status.ACCEPTED,
                },
            )
            Rating.objects.get_or_create(
                service_request=sr3,
                defaults={
                    'score': 5,
                    'comment': 'Excelente trabajo. Llegó puntual y dejó todo limpio.',
                },
            )
            self.stdout.write('  + Solicitud #%d — COMPLETED con valoración 5★' % sr3.pk)

        # 4. Solicitud CANCELLED
        sr4, created4 = ServiceRequest.objects.get_or_create(
            client=cliente2,
            provider=prov2,
            category=cat_elec,
            commune=com_stgo,
            description='Necesito instalar un enchufe nuevo en la cocina.',
            defaults={
                'address': 'Av. Matta 234, Depto 101',
                'status': ServiceRequest.Status.CANCELLED,
            },
        )
        if created4:
            self.stdout.write('  + Solicitud #%d — CANCELLED' % sr4.pk)

        # 5. Solicitud IN_PROGRESS
        if cat_gas and com_provi:
            sr5, created5 = ServiceRequest.objects.get_or_create(
                client=cliente1,
                provider=prov3,
                category=cat_gas,
                commune=com_provi,
                description='Revisión y mantención anual de calefón y estufa.',
                defaults={
                    'address': 'Av. Pedro de Valdivia 1500',
                    'preferred_time': 'Mañana',
                    'status': ServiceRequest.Status.IN_PROGRESS,
                },
            )
            if created5:
                Quote.objects.get_or_create(
                    service_request=sr5,
                    provider=prov3,
                    defaults={
                        'description': 'Mantención preventiva de calefón y estufa '
                                       'con limpieza de quemadores.',
                        'price': 45000,
                        'estimated_duration': '2 horas',
                        'status': Quote.Status.ACCEPTED,
                    },
                )
                self.stdout.write('  + Solicitud #%d — IN_PROGRESS' % sr5.pk)

    # -----------------------------------------------------------------------
    # Reset
    # -----------------------------------------------------------------------

    def _reset(self):
        """Eliminar únicamente usuarios y datos creados por este comando.

        Las relaciones con solicitudes, cotizaciones, valoraciones y perfiles
        se eliminan en cascada. Los usuarios ajenos a la demo se conservan.
        """
        self.stdout.write(self.style.WARNING('Eliminando datos de demostración...'))
        related = ServiceRequest.objects.filter(Q(client__username__in=DEMO_USERNAMES) | Q(provider__username__in=DEMO_USERNAMES))
        if any(model.objects.filter(service_request__in=related).exists() for model in (MaterialExtra, PaymentOrder, ServiceMessage, ServiceDispute, WorkEvidence)):
            raise CommandError('Hay materiales, liquidaciones o mensajes asociados a la demo. Usa una base de pruebas nueva para conservar ese historial.')
        User.objects.filter(username__in=DEMO_USERNAMES).delete()
        self.stdout.write('  Datos eliminados.')
