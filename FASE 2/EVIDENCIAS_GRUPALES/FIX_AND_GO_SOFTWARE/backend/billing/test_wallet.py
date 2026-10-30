from django.test import override_settings
from rest_framework.test import APITestCase
from accounts.models import User
from .models import DemoCard


@override_settings(DEBUG=True, PAYMENTS_DEMO_ENABLED=True)
class WalletTests(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user(username='wallet-client', email='wallet-client@example.test')
        self.client.force_authenticate(self.user)
        self.url='/api/v1/wallet/demo-card/'

    def test_save_is_idempotent_private_and_removable(self):
        for _ in range(2):
            result=self.client.post(self.url,{},format='json')
            self.assertEqual(result.status_code,200)
            self.assertEqual(result.data['card']['last4'],'4242')
            self.assertNotIn('token',result.data['card'])
        self.assertEqual(DemoCard.objects.count(),1)
        other=User.objects.create_user(username='wallet-other', email='wallet-other@example.test')
        self.client.force_authenticate(other)
        self.assertIsNone(self.client.get(self.url).data['card'])
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(self.url).status_code,204)
        self.assertFalse(DemoCard.objects.exists())

    def test_rejects_card_details_and_non_clients(self):
        self.assertEqual(self.client.post(self.url,{'pan':'do-not-store'},format='json').status_code,400)
        self.assertFalse(DemoCard.objects.exists())
        self.user.role='PROVIDER';self.user.save()
        self.assertEqual(self.client.get(self.url).status_code,403)

    @override_settings(DEBUG=False)
    def test_disabled_outside_demo(self):
        self.assertEqual(self.client.post(self.url,{},format='json').status_code,403)
