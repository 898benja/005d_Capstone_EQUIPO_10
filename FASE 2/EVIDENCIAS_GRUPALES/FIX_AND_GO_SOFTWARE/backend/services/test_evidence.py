import base64
import io
import tempfile
from PIL import Image
from django.test import override_settings
from rest_framework.test import APITestCase
from accounts.models import User
from catalog.models import Category, Commune
from .models import ServiceRequest, WorkEvidence


class EvidenceTests(APITestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.settings=override_settings(MEDIA_ROOT=self.directory.name)
        self.settings.enable();self.addCleanup(self.settings.disable)
        self.provider=User.objects.create_user(username='photo-provider',email='photo-provider@example.test',role='PROVIDER')
        self.customer=User.objects.create_user(username='photo-client',email='photo-client@example.test')
        self.other=User.objects.create_user(username='photo-other',email='photo-other@example.test')
        self.job=ServiceRequest.objects.create(provider=self.provider,client=self.customer,
            category=Category.objects.first(),commune=Commune.objects.first(),status='IN_PROGRESS',description='Prueba')
        self.url=f'/api/v1/requests/{self.job.pk}/evidence/'
        image=Image.new('RGB',(20,20),'blue');output=io.BytesIO()
        image.save(output,format='PNG')
        self.payload={'image_base64':base64.b64encode(output.getvalue()).decode(),'caption':'Resultado'}

    def test_private_upload_and_download(self):
        self.client.force_authenticate(self.provider)
        response=self.client.post(self.url,self.payload,format='json')
        self.assertEqual(response.status_code,201)
        photo_url=f"{self.url}{response.data['id']}/"
        self.client.force_authenticate(self.customer)
        photo=self.client.get(photo_url)
        self.assertEqual(photo.status_code,200)
        self.assertEqual(photo['Cache-Control'],'private, no-store')
        with Image.open(io.BytesIO(base64.b64decode(photo.data['image_base64']))) as image:
            self.assertEqual(image.format,'JPEG');self.assertFalse(image.getexif())
        self.assertEqual(self.client.post(self.url,self.payload,format='json').status_code,404)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(photo_url).status_code,404)
        self.assertEqual(self.client.get(self.url).status_code,404)

    def test_invalid_image_state_and_limit(self):
        self.client.force_authenticate(self.provider)
        self.assertEqual(self.client.post(self.url,{'image_base64':'not an image'},format='json').status_code,400)
        self.assertFalse(WorkEvidence.objects.exists())
        self.job.status='PENDING';self.job.save()
        self.assertEqual(self.client.post(self.url,self.payload,format='json').status_code,400)
        self.job.status='IN_PROGRESS';self.job.save()
        for _ in range(10):
            self.assertEqual(self.client.post(self.url,self.payload,format='json').status_code,201)
        self.assertEqual(self.client.post(self.url,self.payload,format='json').status_code,400)
