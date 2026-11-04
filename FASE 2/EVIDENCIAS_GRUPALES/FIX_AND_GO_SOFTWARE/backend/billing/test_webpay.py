from unittest.mock import patch
from django.test import override_settings
from rest_framework.test import APITestCase
from .tests import BillingTests
from .models import PaymentOrder, WebpayAttempt
from .webpay import GatewayUnavailable
from django.urls import reverse
from accounts.models import User
from .models import ServiceDispute, ProviderWarning
from .disputes import resolve


@override_settings(DEBUG=True, PAYMENTS_DEMO_ENABLED=True, WEBPAY_INTEGRATION_ENABLED=True,
                   WEBPAY_RETURN_URL='http://testserver/api/v1/webpay/return/')
class WebpayTests(APITestCase):
    setUp = BillingTests.setUp
    post = BillingTests.post
    get = BillingTests.get

    def start(self):
        with patch('billing.webpay.call', return_value={'token': 'a'*64, 'url':'https://webpay3gint.transbank.cl/webpayserver/initTransaction'}):
            res = self.post(self.customer, 'webpay-start')
        self.assertEqual(res.status_code, 200, res.data)
        return WebpayAttempt.objects.get()

    def test_approval_verified_idempotent_and_chat_unlocked(self):
        attempt = self.start()
        self.assertEqual(self.get(self.customer, 'service-messages').status_code, 403)
        approved = {'status':'AUTHORIZED', 'response_code':0, 'amount':35000, 'buy_order':attempt.buy_order}
        with patch('billing.webpay.call', side_effect=[{'status':'INITIALIZED'}, approved]) as gateway:
            self.assertEqual(self.client.get('/api/v1/webpay/return/', {'token_ws':attempt.token}).status_code, 200)
            self.assertEqual(gateway.call_count, 2)
        with patch('billing.webpay.call') as gateway:
            self.client.get('/api/v1/webpay/return/', {'token_ws':attempt.token})
            gateway.assert_not_called()
        self.assertEqual(PaymentOrder.objects.get().status, 'DEMO_PAID')
        self.assertEqual(self.get(self.provider, 'service-messages').status_code, 200)

    def test_amount_mismatch_cannot_unlock_chat(self):
        attempt = self.start()
        with patch('billing.webpay.call', return_value={'status':'AUTHORIZED', 'response_code':0, 'amount':1, 'buy_order':attempt.buy_order}):
            self.client.get('/api/v1/webpay/return/', {'token_ws':attempt.token})
        self.assertEqual(PaymentOrder.objects.get().status, 'FAILED')
        self.assertEqual(self.get(self.customer, 'service-messages').status_code, 403)

    def test_pending_gateway_cannot_be_simulated_or_cancelled(self):
        self.start()
        self.assertEqual(self.post(self.customer,'demo-payment-result',{'outcome':'approved'}).status_code,409)
        self.assertEqual(self.post(self.customer,'request-cancel').status_code,409)
        self.assertEqual(self.post(self.other,'webpay-start').status_code,404)

    def test_network_failure_preserves_pending_attempt(self):
        attempt = self.start()
        with patch('billing.webpay.call', side_effect=GatewayUnavailable()):
            res = self.client.get('/api/v1/webpay/return/', {'token_ws':attempt.token})
        self.assertEqual(res.status_code,503)
        attempt.refresh_from_db(); self.assertFalse(attempt.finished)
        self.assertEqual(PaymentOrder.objects.get().status,'PENDING')

    def test_abort_then_cancel_never_allows_late_payment(self):
        attempt = self.start()
        with patch('billing.webpay.call', return_value={'status':'INITIALIZED'}):
            self.client.get('/api/v1/webpay/return/', {'TBK_TOKEN':attempt.token})
        self.assertEqual(self.post(self.customer,'request-cancel').status_code,200)
        self.assertEqual(self.post(self.customer,'checkout').status_code,409)
        with patch('billing.webpay.call') as gateway:
            self.client.get('/api/v1/webpay/return/', {'token_ws':attempt.token})
            gateway.assert_not_called()
        self.assertEqual(PaymentOrder.objects.get().status,'FAILED')

    def test_simulator_cannot_charge_cancelled_request(self):
        self.post(self.customer,'checkout')
        self.assertEqual(self.post(self.customer,'request-cancel').status_code,200)
        self.assertEqual(self.post(self.customer,'demo-payment-result',{'outcome':'approved'}).status_code,409)

    def test_disabled_gateway_and_unknown_token(self):
        with self.settings(WEBPAY_INTEGRATION_ENABLED=False):
            self.assertEqual(self.post(self.customer,'webpay-start').status_code,403)
        self.assertEqual(self.client.get('/api/v1/webpay/return/?token_ws=unknown').status_code,404)

    def test_double_start_reuses_session(self):
        attempt = self.start()
        with patch('billing.webpay.call') as gateway:
            self.assertEqual(self.post(self.customer,'webpay-start').status_code,200)
            gateway.assert_not_called()
        self.assertEqual(WebpayAttempt.objects.count(),1)

    def test_timeout_matches_order_and_checks_gateway_without_commit(self):
        attempt = self.start()
        with patch('billing.webpay.call', return_value={'status':'FAILED'}) as gateway:
            result = self.client.get('/api/v1/webpay/return/', {
                'TBK_ID_SESION':str(attempt.order_id), 'TBK_ORDEN_COMPRA':attempt.buy_order})
        self.assertEqual(result.status_code, 200)
        gateway.assert_called_once_with('GET', '/' + attempt.token)
        attempt.refresh_from_db()
        self.assertTrue(attempt.finished)
        self.assertEqual(PaymentOrder.objects.get().status, 'FAILED')

    def test_payment_page_explains_test_money_and_uses_official_host(self):
        attempt = self.start()
        response = self.client.get('/api/v1/webpay/launch/', {'token':attempt.token})
        self.assertContains(response, 'Dinero real que pagarás: $0')
        self.assertContains(response, '$35.000')
        self.assertContains(response, 'https://webpay3gint.transbank.cl/webpayserver/initTransaction')
        self.assertEqual(response['Cache-Control'], 'no-store')

    def test_address_hidden_until_verified_payment(self):
        self.sr.address = 'Dirección privada de prueba'; self.sr.latitude=-33.45; self.sr.longitude=-70.66; self.sr.save()
        self.client.force_authenticate(self.provider)
        path = reverse('request-detail', args=[self.sr.pk])
        self.assertIsNone(self.client.get(path).data['address'])
        self.assertIsNone(self.client.get('/api/v1/provider/dashboard/').data['recent'][0]['latitude'])
        attempt = self.start()
        with patch('billing.webpay.call', return_value={'status':'AUTHORIZED', 'response_code':0, 'amount':35000, 'buy_order':attempt.buy_order}):
            self.client.get('/api/v1/webpay/return/', {'token_ws':attempt.token})
        self.client.force_authenticate(self.provider)
        self.assertEqual(self.client.get(path).data['address'], self.sr.address)
        self.assertIsNotNone(self.client.get('/api/v1/provider/dashboard/').data['recent'][0]['latitude'])

    def test_gateway_refund_retries_without_duplicate_warning(self):
        attempt = self.start()
        order = attempt.order; order.status='DEMO_PAID'; order.save()
        attempt.finished=True; attempt.save()
        reviewer = User.objects.create_user(username='reviewer',email='reviewer@example.test',is_staff=True)
        dispute = ServiceDispute.objects.create(service_request=self.sr, reason='Trabajo no realizado en prueba')
        with patch('billing.webpay.call', side_effect=GatewayUnavailable()):
            with self.assertRaises(GatewayUnavailable):
                resolve(dispute.id, reviewer, 'REFUND', 'Antecedentes revisados por el equipo')
        order.refresh_from_db(); self.assertEqual(order.status,'DEMO_PAID')
        self.assertFalse(ProviderWarning.objects.exists())
        # Gateway already reversed it before a connection loss. Reconcile safely.
        with patch('billing.webpay.call', return_value={'status':'REVERSED'}) as gateway:
            resolve(dispute.id, reviewer, 'REFUND', 'Antecedentes revisados por el equipo')
            resolve(dispute.id, reviewer, 'REFUND', 'Antecedentes revisados por el equipo')
            self.assertEqual(gateway.call_count,1)
        order.refresh_from_db(); self.assertEqual(order.status,'DEMO_REFUNDED')
        self.assertEqual(ProviderWarning.objects.count(),1)
