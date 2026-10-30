"""Regresión del recorrido principal y sus transiciones inválidas."""
from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework.test import APITestCase
from accounts.models import ProviderProfile, User
from catalog.models import Category, Commune
from .models import Quote, ServiceRequest
from django.test import override_settings


class RequestWorkflowTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='client', email='client@example.test')
        self.provider = User.objects.create_user(username='provider', email='provider@example.test', role='PROVIDER')
        self.outsider = User.objects.create_user(username='outsider', email='outsider@example.test')
        self.category = Category.objects.first()
        self.commune = Commune.objects.first()
        self.profile = ProviderProfile.objects.create(user=self.provider, display_name='Demo')
        self.profile.categories.add(self.category)
        self.profile.communes.add(self.commune)
        self.sr = ServiceRequest.objects.create(
            client=self.customer, provider=self.provider, category=self.category,
            commune=self.commune, description='Filtración de demostración', address='Dirección ficticia',
        )

    def post_as(self, user, route, data=None):
        self.client.force_authenticate(user)
        return self.client.post(reverse(route, args=[self.sr.pk]), data or {}, format='json')

    def quote(self):
        return self.post_as(self.provider, 'quote-create-or-get', {
            'description': 'Reparación de prueba', 'price': 35000,
        })

    def test_create_and_accept_is_idempotent(self):
        self.assertEqual(self.quote().status_code, 201)
        for _ in range(2):
            self.assertEqual(self.post_as(self.customer, 'quote-accept').status_code, 200)
        self.sr.refresh_from_db()
        self.assertEqual(self.sr.status, 'ACCEPTED')
        self.assertEqual(Quote.objects.get().status, 'ACCEPTED')
        self.assertEqual(self.post_as(self.customer, 'request-cancel').status_code, 409)

    def test_cancellation_prevents_accept(self):
        self.quote()
        response = self.post_as(self.customer, 'request-cancel')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['quote'])
        self.assertEqual(Quote.objects.get().status, 'WITHDRAWN')
        self.assertEqual(self.post_as(self.customer, 'quote-accept').status_code, 409)
        self.sr.refresh_from_db()
        self.assertEqual(self.sr.status, 'CANCELLED')

    def test_rejection_allows_new_quote(self):
        self.quote()
        self.assertEqual(self.post_as(self.customer, 'quote-reject').status_code, 200)
        self.assertEqual(self.quote().status_code, 201)
        self.assertEqual(Quote.objects.filter(status='SUBMITTED').count(), 1)

    def test_withdraw_allows_new_quote(self):
        self.quote()
        self.assertEqual(self.post_as(self.provider, 'quote-withdraw').status_code, 200)
        self.assertEqual(self.quote().status_code, 201)

    def test_duplicate_quote_conflicts(self):
        self.quote()
        self.assertEqual(self.quote().status_code, 409)
        self.assertEqual(Quote.objects.count(), 1)

    def test_inconsistent_state_rolls_back(self):
        ServiceRequest.objects.filter(pk=self.sr.pk).update(status='QUOTED')
        self.assertEqual(self.post_as(self.customer, 'quote-accept').status_code, 409)
        self.sr.refresh_from_db()
        self.assertEqual(self.sr.status, 'QUOTED')

    def test_database_rejects_duplicate_and_zero_price(self):
        self.quote()
        for price in [0, 100]:
            with self.subTest(price=price), self.assertRaises(IntegrityError), transaction.atomic():
                Quote.objects.create(service_request=self.sr, provider=self.provider,
                                     description='Duplicada', price=price)

    def test_outsider_cannot_read_or_change(self):
        self.quote()
        self.client.force_authenticate(self.outsider)
        self.assertEqual(self.client.get(reverse('request-detail', args=[self.sr.pk])).status_code, 404)
        for route in ['quote-accept', 'quote-reject', 'request-cancel']:
            self.assertEqual(self.post_as(self.outsider, route).status_code, 404)

    def test_wrong_role_cannot_accept_or_quote(self):
        self.quote()
        self.assertEqual(self.post_as(self.provider, 'quote-accept').status_code, 403)
        self.assertEqual(self.post_as(self.customer, 'quote-create-or-get', {'price': 100}).status_code, 403)

    def test_list_is_scoped_and_excludes_private_address(self):
        for user, expected in [(self.customer, 1), (self.provider, 1), (self.outsider, 0)]:
            self.client.force_authenticate(user)
            response = self.client.get(reverse('request-list-create'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['count'], expected)
            self.assertIn('results', response.data)
            for row in response.data['results']:
                self.assertNotIn('address', row)

    def test_create_checks_coverage(self):
        self.client.force_authenticate(self.customer)
        payload = dict(provider_id=self.provider.pk, category_id=self.category.pk,
                       commune_id=self.commune.pk, description='Solicitud de demostración')
        self.assertEqual(self.client.post(reverse('request-list-create'), payload).status_code, 201)
        self.profile.communes.clear()
        self.assertEqual(self.client.post(reverse('request-list-create'), payload).status_code, 400)
        self.profile.communes.add(self.commune)
        self.profile.categories.clear()
        self.assertEqual(self.client.post(reverse('request-list-create'), payload).status_code, 400)

    def test_invalid_price_does_not_change_request(self):
        response = self.post_as(self.provider, 'quote-create-or-get', {'price': 0, 'description': 'Demo'})
        self.assertEqual(response.status_code, 400)
        self.sr.refresh_from_db()
        self.assertEqual(self.sr.status, 'PENDING')

    @override_settings(DEBUG=True, PAYMENTS_DEMO_ENABLED=True)
    def test_complete_service_and_rate_full_flow(self):
        self.quote()
        self.post_as(self.customer, 'quote-accept')
        self.assertEqual(self.post_as(self.provider,'request-start').status_code,409)
        self.client.force_authenticate(self.customer)
        self.client.post('/api/v1/wallet/demo-card/',{},format='json')
        self.assertEqual(self.post_as(self.customer,'checkout').status_code,201)
        self.assertEqual(self.post_as(self.customer,'demo-payment-result',{'outcome':'approved'}).status_code,200)
        self.assertEqual(self.post_as(self.provider, 'request-start').status_code, 200)
        self.assertEqual(self.post_as(self.customer, 'request-complete').status_code, 409)
        # Foto real creada y subida mediante el contrato API, en almacenamiento temporal.
        import io, base64, tempfile
        from PIL import Image
        image=Image.new('RGB',(10,10),'white');buffer=io.BytesIO();image.save(buffer,format='PNG')
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            self.client.force_authenticate(self.provider)
            upload=self.client.post(f'/api/v1/requests/{self.sr.pk}/evidence/',{'image_base64':base64.b64encode(buffer.getvalue()).decode()},format='json')
            self.assertEqual(upload.status_code,201)
            self.assertEqual(self.post_as(self.provider,'request-complete').status_code,403)
            self.assertEqual(self.post_as(self.customer,'request-complete').status_code,200)

        response = self.post_as(self.customer, 'request-rating', {
            'score': 5,
            'comment': 'Servicio de prueba completado correctamente.',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['score'], 5)
        self.assertEqual(
            self.post_as(self.customer, 'request-rating', {'score': 4}).status_code,
            409,
        )

        self.client.force_authenticate(self.outsider)
        self.assertEqual(
            self.client.get(reverse('request-rating', args=[self.sr.pk])).status_code,
            404,
        )

    def test_service_cannot_complete_before_start(self):
        self.quote()
        self.post_as(self.customer, 'quote-accept')
        self.assertEqual(self.post_as(self.customer, 'request-complete').status_code, 409)
