"""QA del contrato público: importes, permisos, persistencia y reintentos."""
from django.test import override_settings
from django.urls import reverse
from django.db import transaction, IntegrityError
from rest_framework.test import APITestCase
from accounts.models import User, ProviderProfile
from catalog.models import Category, Commune
from services.models import ServiceRequest, Quote
from .models import MaterialExtra, PaymentOrder, DemoCard

@override_settings(DEBUG=True, PAYMENTS_DEMO_ENABLED=True)
class BillingTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='billing-client', email='billing-client@example.test', first_name='Cliente')
        self.provider = User.objects.create_user(username='billing-provider', email='billing-provider@example.test', role='PROVIDER')
        self.other = User.objects.create_user(username='billing-other', email='billing-other@example.test')
        self.category, self.commune = Category.objects.first(), Commune.objects.first()
        self.profile = ProviderProfile.objects.create(user=self.provider, display_name='Prestador prueba', phone='+56912345678')
        self.profile.categories.add(self.category)
        self.profile.communes.add(self.commune)
        self.sr = ServiceRequest.objects.create(client=self.customer, provider=self.provider, category=self.category, commune=self.commune, description='Servicio de prueba', status='ACCEPTED')
        DemoCard.objects.create(user=self.customer)
        Quote.objects.create(service_request=self.sr, provider=self.provider, description='Servicio con impuesto incluido', price=35000, status='ACCEPTED')

    def post(self, user, route, data=None, material=None):
        self.client.force_authenticate(user)
        args = [self.sr.pk] + ([material] if material else [])
        return self.client.post(reverse(route, args=args), data or {}, format='json')

    def get(self, user, route):
        self.client.force_authenticate(user)
        return self.client.get(reverse(route, args=[self.sr.pk]))

    def extra(self):
        res = self.post(self.provider, 'materials', {'description':'Repuesto de prueba', 'quantity':2, 'unit_price':2500})
        self.assertEqual(res.status_code, 201, res.data)
        return res.data['id']

    def approve(self, pk):
        return self.post(self.customer, 'material-decision', {'decision':'APPROVED'}, pk)

    def test_complete_flow_with_materials_retry_receipt_and_messages(self):
        mid = self.extra()
        self.assertEqual(self.post(self.customer, 'checkout').status_code, 409)
        self.assertEqual(self.approve(mid).status_code, 200)
        first = self.post(self.customer, 'checkout')
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(first.data['total'], 40000)
        self.assertEqual(first.data['commission_amount'], 10500)
        self.assertEqual(first.data['provider_amount'], 29500)
        self.assertEqual(first.data['net_amount'] + first.data['vat_amount'], 40000)
        self.assertEqual(self.post(self.customer, 'checkout').data['id'], first.data['id'])
        self.assertEqual(PaymentOrder.objects.count(), 1)
        rejected = self.post(self.customer, 'demo-payment-result', {'outcome':'rejected'})
        self.assertEqual(rejected.data['status'], 'FAILED')
        self.assertEqual(self.get(self.customer, 'receipt').status_code, 404)
        self.assertEqual(self.get(self.customer, 'service-messages').status_code, 403)
        for _ in range(2):
            paid = self.post(self.customer, 'demo-payment-result', {'outcome':'approved'})
            self.assertEqual(paid.data['status'], 'DEMO_PAID')
        receipt = self.get(self.provider, 'receipt')
        self.assertEqual(receipt.status_code, 200)
        self.assertFalse(receipt.data['fiscal_document'])
        self.assertEqual(receipt.data['snapshot']['materials'][0]['total'], 5000)
        self.assertEqual(self.post(self.customer, 'service-messages', {'text':'Consulta de prueba'}).status_code, 201)
        self.assertEqual(self.post(self.provider, 'service-messages', {'text':'Respuesta de prueba'}).status_code, 201)
        self.assertEqual(self.get(self.customer, 'service-messages').data['count'], 2)
        self.assertEqual(self.post(self.customer, 'demo-payment-result', {'outcome':'rejected'}).status_code, 409)

    def test_rejected_materials_are_not_charged(self):
        mid = self.extra()
        self.post(self.customer, 'material-decision', {'decision':'REJECTED'}, mid)
        self.assertEqual(self.post(self.customer, 'checkout').data['total'], 35000)

    def test_decisions_are_idempotent_but_cannot_be_reversed(self):
        mid = self.extra()
        self.assertEqual(self.approve(mid).status_code, 200)
        self.assertEqual(self.approve(mid).status_code, 200)
        self.assertEqual(self.post(self.customer, 'material-decision', {'decision':'REJECTED'}, mid).status_code, 409)

    def test_frozen_order_cannot_add_or_change_materials_even_after_failure(self):
        mid = self.extra()
        self.approve(mid)
        self.post(self.customer, 'checkout')
        self.post(self.customer, 'demo-payment-result', {'outcome':'rejected'})
        self.assertEqual(self.post(self.provider, 'materials', {'description':'Otro', 'quantity':1,'unit_price':1}).status_code, 409)
        self.assertEqual(self.approve(mid).status_code, 409)

    def test_outsider_and_wrong_roles_cannot_operate(self):
        mid = self.extra()
        for route in ['materials','billing-summary','receipt','service-messages']:
            self.assertEqual(self.get(self.other, route).status_code, 404)
        for user in [self.other, self.provider]:
            self.assertEqual(self.post(user, 'checkout').status_code, 404)
            self.assertEqual(self.post(user, 'material-decision', {'decision':'APPROVED'}, mid).status_code, 404)
            self.assertEqual(self.post(user, 'demo-payment-result', {'outcome':'approved'}).status_code, 404)
        self.assertEqual(self.post(self.customer, 'materials', {'description':'Test','quantity':1,'unit_price':100}).status_code, 404)

    def test_disabled_or_non_debug_cannot_simulate_a_payment(self):
        for flags in [{'DEBUG':False, 'PAYMENTS_DEMO_ENABLED':True}, {'DEBUG':True, 'PAYMENTS_DEMO_ENABLED':False}]:
            with self.settings(**flags):
                self.assertFalse(self.get(self.customer,'billing-summary').data['demo_enabled'])
                self.assertEqual(self.post(self.customer,'checkout').status_code,403)
                self.assertEqual(self.post(self.customer,'demo-payment-result',{'outcome':'approved'}).status_code,403)
        self.assertFalse(PaymentOrder.objects.exists())

    def test_tampered_amounts_states_and_card_data_are_rejected(self):
        for body in [{'total':1}, {'status':'DEMO_PAID'}, {'card_number':'4242424242424242'}]:
            self.assertEqual(self.post(self.customer,'checkout',body).status_code,400)
        self.assertFalse(PaymentOrder.objects.exists())
        self.assertEqual(self.post(self.provider,'materials',{'description':'Test','quantity':1,'unit_price':100,'status':'APPROVED'}).status_code,400)

    def test_amount_bounds_and_total_overflow(self):
        for quantity, price in [(0,1),(1,0),(-1,1),(1,100000001),(10001,1)]:
            self.assertEqual(self.post(self.provider,'materials',{'description':'Test','quantity':quantity,'unit_price':price}).status_code,400)
        m = MaterialExtra.objects.create(service_request=self.sr,description='Exceso',quantity=10000,unit_price=100000000,status='APPROVED')
        self.assertEqual(self.post(self.customer,'checkout').status_code,400)
        self.assertFalse(PaymentOrder.objects.exists())

    def test_checkout_must_precede_work_and_chat_waits_for_payment(self):
        self.sr.status='IN_PROGRESS'; self.sr.save()
        self.assertEqual(self.post(self.customer,'checkout').status_code,409)
        self.assertEqual(self.post(self.customer,'service-messages',{'text':'Antes de pagar'}).status_code,403)
        self.assertEqual(self.post(self.customer,'demo-payment-result',{'outcome':'approved'}).status_code,404)

    def test_private_profile_persists_and_cannot_elevate_role(self):
        self.client.force_authenticate(self.customer)
        data={'first_name':'Persona', 'last_name':'Prueba','phone':'+56912345678','default_address':'Dirección ficticia','default_commune':self.commune.pk}
        response=self.client.patch(reverse('me'),data,format='json')
        self.assertEqual(response.status_code,200,response.data)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.default_address,data['default_address'])
        self.assertEqual(self.client.get(reverse('me')).data['default_commune'],self.commune.pk)
        for data in [{'role':'PROVIDER'},{'is_staff':True},{'phone':'--------'},{'first_name':' '},{'card_number':'4242424242424242'}]:
            self.assertEqual(self.client.patch(reverse('me'),data,format='json').status_code,400)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.role,'CLIENT')

    def test_invalid_filters_are_client_errors(self):
        self.client.force_authenticate(self.customer)
        for query in ['category=abc','date_from=no-date','status=UNKNOWN','provider=-2','date_from=2026-10-20&date_to=2026-10-19']:
            self.assertEqual(self.client.get('/api/v1/requests/?'+query).status_code,400,query)

    def test_public_catalog_has_no_phone_or_private_profile(self):
        self.client.force_authenticate(self.customer)
        response=self.client.get('/api/v1/providers/')
        self.assertEqual(response.status_code,200)
        record=response.data['results'][0]
        self.assertEqual(record['phone'],'')
        self.assertNotIn('email',record)
        self.assertNotIn('default_address',record)
        self.provider.is_active=False; self.provider.save()
        self.assertEqual(self.client.get('/api/v1/providers/').data['count'],0)

    def test_database_constraints_on_duplicate_payment_and_material_quantity(self):
        self.post(self.customer,'checkout')
        order=PaymentOrder.objects.get()
        with self.assertRaises(IntegrityError), transaction.atomic():
            order.pk=None; order.save(force_insert=True)
        with self.assertRaises(IntegrityError), transaction.atomic():
            MaterialExtra.objects.create(service_request=self.sr,description='Inválido',quantity=0,unit_price=1)
