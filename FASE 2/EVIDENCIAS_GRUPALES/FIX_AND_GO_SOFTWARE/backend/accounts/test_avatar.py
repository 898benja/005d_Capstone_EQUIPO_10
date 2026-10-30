import base64
import io
from PIL import Image
from rest_framework.test import APITestCase
from accounts.models import ProviderProfile, User
from catalog.models import Category, Commune
from services.models import ServiceRequest, Rating


class PublicProfileTests(APITestCase):
    def test_avatar_and_real_rating_average(self):
        provider=User.objects.create_user(username='portrait-p',email='portrait-p@example.test',role='PROVIDER')
        customer=User.objects.create_user(username='portrait-c',email='portrait-c@example.test')
        profile=ProviderProfile.objects.create(user=provider,display_name='Perfil QA')
        self.client.force_authenticate(customer)
        url='/api/v1/auth/me/provider-profile/avatar/'
        self.assertEqual(self.client.post(url,{},format='json').status_code,403)
        self.client.force_authenticate(provider)
        self.assertEqual(self.client.post(url,{'image_base64':'invalid'},format='json').status_code,400)
        picture=Image.new('RGB',(50,40),'blue');buffer=io.BytesIO();picture.save(buffer,format='PNG')
        result=self.client.post(url,{'image_base64':base64.b64encode(buffer.getvalue()).decode()},format='json')
        self.assertEqual(result.status_code,200)
        self.assertTrue(result.data['avatar'].startswith('data:image/jpeg;base64,'))
        self.client.force_authenticate(customer)
        detail=self.client.get(f'/api/v1/providers/{profile.pk}/').data
        self.assertIsNone(detail['avg_rating']);self.assertEqual(detail['rating_count'],0)
        for score in [4,5]:
            job=ServiceRequest.objects.create(client=customer,provider=provider,category=Category.objects.first(),commune=Commune.objects.first(),description='QA',status='COMPLETED')
            Rating.objects.create(service_request=job,score=score)
        for path in ['/api/v1/providers/',f'/api/v1/providers/{profile.pk}/']:
            data=self.client.get(path).data
            row=data['results'][0] if 'results' in data else data
            self.assertEqual(row['avg_rating'],4.5);self.assertEqual(row['rating_count'],2)
            self.assertTrue(row['avatar'])
        self.client.force_authenticate(provider)
        self.assertEqual(self.client.delete(url,{},format='json').data['avatar'],'')
