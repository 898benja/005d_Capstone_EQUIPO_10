from rest_framework.test import APITestCase
from accounts.models import User
from catalog.models import Category, Commune
from .models import ServiceRequest


class DashboardTests(APITestCase):
    def test_private_dashboard_counts_and_customers(self):
        provider = User.objects.create_user(username='provider-home', email='provider-home@example.test', role='PROVIDER')
        other = User.objects.create_user(username='other-home', email='other-home@example.test', role='PROVIDER')
        customer = User.objects.create_user(username='customer-home', email='customer-home@example.test', first_name='Cliente')
        for owner in [provider, other]:
            ServiceRequest.objects.create(provider=owner,client=customer,
                category=Category.objects.first(),commune=Commune.objects.first(),
                description='Prueba',status='COMPLETED',latitude=-33.45,longitude=-70.67)
        url='/api/v1/provider/dashboard/'
        self.assertEqual(self.client.get(url).status_code,401)
        self.client.force_authenticate(customer)
        self.assertEqual(self.client.get(url).status_code,403)
        self.client.force_authenticate(provider)
        result=self.client.get(url)
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.data['counts'],{'COMPLETED':1})
        self.assertEqual(len(result.data['recent']),1)
        self.assertEqual(result.data['customers'][0]['completed_jobs'],1)
        self.assertNotIn('email',str(result.data))
