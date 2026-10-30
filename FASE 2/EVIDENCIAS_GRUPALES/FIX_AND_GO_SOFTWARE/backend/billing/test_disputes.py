from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from accounts.models import User, ProviderProfile
from catalog.models import Category, Commune
from services.models import ServiceRequest, Quote
from .models import DemoCard, PaymentOrder, ProviderWarning


@override_settings(DEBUG=True,PAYMENTS_DEMO_ENABLED=True)
class DisputeTests(APITestCase):
    def setUp(self):
        self.customer=User.objects.create_user(username='dispute-c',email='dispute-c@example.test')
        self.provider=User.objects.create_user(username='dispute-p',email='dispute-p@example.test',role='PROVIDER')
        self.admin=User.objects.create_user(username='dispute-admin',email='dispute-a@example.test',is_staff=True)
        self.other=User.objects.create_user(username='dispute-other',email='dispute-o@example.test')
        ProviderProfile.objects.create(user=self.provider,display_name='Prestador QA')
        DemoCard.objects.create(user=self.customer)

    def post(self,user,path,data=None):
        self.client.force_authenticate(user)
        return self.client.post('/api/v1/'+path,data or {},format='json')

    def paid(self):
        job=ServiceRequest.objects.create(client=self.customer,provider=self.provider,
            category=Category.objects.first(),commune=Commune.objects.first(),status='ACCEPTED',description='Caso QA')
        Quote.objects.create(service_request=job,provider=self.provider,description='Servicio QA',price=10001,status='ACCEPTED')
        self.assertEqual(self.post(self.customer,f'requests/{job.id}/checkout/').status_code,201)
        self.assertEqual(self.post(self.customer,f'requests/{job.id}/payment/demo-result/',{'outcome':'approved'}).status_code,200)
        return job

    def open(self,job):
        result=self.post(self.customer,f'requests/{job.id}/dispute/',{'reason':'El prestador no realizó el trabajo acordado.'})
        self.assertEqual(result.status_code,201)
        return result.data['id']

    def test_refund_is_reviewed_once_and_cannot_be_charged_again(self):
        job=self.paid();dispute=self.open(job)
        self.assertFalse(ProviderWarning.objects.exists())
        self.assertEqual(self.post(self.provider,f'requests/{job.id}/start/').status_code,409)
        path=f'admin/disputes/{dispute}/review/'
        data={'decision':'REFUND','note':'Se revisaron los antecedentes con las partes.'}
        self.assertEqual(self.post(self.customer,path,data).status_code,403)
        for _ in range(2):
            self.assertEqual(self.post(self.admin,path,data).status_code,200)
        self.assertEqual(ProviderWarning.objects.count(),1)
        self.assertEqual(PaymentOrder.objects.get(service_request=job).status,'DEMO_REFUNDED')
        self.assertEqual(self.post(self.customer,f'requests/{job.id}/payment/demo-result/',{'outcome':'approved'}).status_code,409)
        self.assertEqual(self.post(self.provider,f'requests/{job.id}/messages/',{'text':'No debe enviarse'}).status_code,403)
        self.assertEqual(self.post(self.other,f'requests/{job.id}/dispute/',{'reason':'No soy parte del servicio.'}).status_code,404)

    def test_three_confirmed_warnings_disable_provider_and_revoke_token(self):
        Token.objects.create(user=self.provider)
        for index in range(3):
            job=self.paid();dispute=self.open(job)
            result=self.post(self.admin,f'admin/disputes/{dispute}/review/',{'decision':'REFUND','note':'Incumplimiento confirmado mediante revisión.'})
            self.assertEqual(result.status_code,200)
            self.provider.refresh_from_db()
            self.assertEqual(self.provider.is_active,index<2)
        self.assertEqual(ProviderWarning.objects.count(),3)
        self.assertFalse(Token.objects.filter(user=self.provider).exists())
        self.assertTrue(User.objects.filter(pk=self.provider.pk).exists())
        self.assertFalse(ProviderProfile.objects.get(user=self.provider).is_active)

    def test_rejection_does_not_refund_or_warn(self):
        job=self.paid();dispute=self.open(job)
        self.assertEqual(self.post(self.admin,f'admin/disputes/{dispute}/review/',{'decision':'REJECT','note':'Trabajo realizado según revisión de antecedentes.'}).status_code,200)
        self.assertFalse(ProviderWarning.objects.exists())
        self.assertEqual(PaymentOrder.objects.get(service_request=job).status,'DEMO_PAID')
        self.assertEqual(self.post(self.provider,f'requests/{job.id}/start/').status_code,200)

    def test_wallet_required_and_commission_rounding(self):
        job=self.paid()
        order=PaymentOrder.objects.get(service_request=job)
        self.assertEqual(order.commission_amount,3000)
        self.assertEqual(order.provider_amount,7001)
        DemoCard.objects.filter(user=self.customer).delete()
        order.status='PENDING';order.save()
        self.assertEqual(self.post(self.customer,f'requests/{job.id}/payment/demo-result/',{'outcome':'approved'}).status_code,409)
