from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase
from accounts.models import ProviderProfile, User
from .models import Category, Commune
from .geo import distance_km


class NearbyTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(username='map-client', email='map-client@example.test')
        cls.category, cls.commune = Category.objects.first(), Commune.objects.first()
        cls.profiles = []
        for i,lat in enumerate([-33.449, -33.47, -33.75]):
            user=User.objects.create_user(username=f'map-{i}',email=f'map-{i}@example.test',role='PROVIDER')
            p=ProviderProfile.objects.create(user=user,display_name=f'Provider {i}',latitude=lat,longitude=-70.6693,map_visible=True)
            p.categories.add(cls.category);p.communes.add(cls.commune)
            cls.profiles.append(p)

    def setUp(self):
        self.client.force_authenticate(self.customer)

    def search(self, **kwargs):
        return self.client.get('/api/v1/providers/', {'latitude':-33.4489,'longitude':-70.6693,'radius_km':5,**kwargs})

    def test_distance_and_order_pagination(self):
        response=self.search(page_size=1)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.data['count'],2)
        self.assertEqual(response.data['results'][0]['id'],self.profiles[0].id)
        self.assertLess(response.data['results'][0]['distance_km'],0.1)
        self.assertIsNotNone(response.data['next'])
        self.assertEqual(self.search(page=2,page_size=1).data['results'][0]['id'],self.profiles[1].id)

    def test_no_location_is_not_invented_and_private_is_hidden(self):
        p=self.profiles[0];p.map_visible=False;p.save()
        self.assertEqual(self.search().data['count'],1)
        data=self.client.get(f'/api/v1/providers/{p.pk}/').data
        self.assertIsNone(data['latitude']);self.assertIsNone(data['longitude'])
        p.latitude=None;p.longitude=None;p.save()
        self.assertEqual(self.search().data['count'],1)

    def test_invalid_inputs_are_400(self):
        for args in [{'latitude':'nan'},{'longitude':'inf'},{'radius_km':'nan'},
                     {'radius_km':0},{'radius_km':31},{'latitude':0},{'longitude':'bad'}]:
            with self.subTest(args=args):self.assertEqual(self.search(**args).status_code,400)
        self.assertEqual(self.client.get('/api/v1/providers/',{'latitude':-33.4}).status_code,400)

    def test_auth_inactive_and_filters(self):
        self.assertEqual(self.search(category='missing').data['count'],0)
        self.assertEqual(self.search(commune='missing').data['count'],0)
        p=self.profiles[0];p.user.is_active=False;p.user.save()
        self.assertEqual(self.search().data['count'],1)
        self.client.force_authenticate(None)
        self.assertEqual(self.search().status_code,401)

    def test_owner_can_publish_hide_and_cannot_publish_invalid_point(self):
        url='/api/v1/auth/me/provider-profile/'
        self.assertEqual(self.client.patch(url,{'map_visible':True},format='json').status_code,403)
        self.client.force_authenticate(self.profiles[0].user)
        self.assertEqual(self.client.patch(url,{'latitude':0},format='json').status_code,400)
        self.assertEqual(self.client.patch(url,{'latitude':None},format='json').status_code,400)
        response=self.client.patch(url,{'latitude':None,'longitude':None,'map_visible':False},format='json')
        self.assertEqual(response.status_code,200)
        self.assertEqual(self.client.patch(url,{'map_visible':True},format='json').status_code,400)
        self.assertEqual(self.client.patch(url,{'latitude':-33.45,'longitude':-70.67,'map_visible':True},format='json').status_code,200)

    def test_database_rejects_partial_or_outside_point(self):
        for fields in [{'latitude':None},{'latitude':90},{'longitude':0}]:
            with self.subTest(fields=fields),self.assertRaises(IntegrityError),transaction.atomic():
                ProviderProfile.objects.filter(pk=self.profiles[0].pk).update(**fields)

    def test_request_point_is_saved_only_in_private_detail(self):
        response=self.client.post('/api/v1/requests/',{
            'provider_id':self.profiles[0].user_id,'category_id':self.category.pk,'commune_id':self.commune.pk,
            'description':'Solicitud sintética de mapa','latitude':-33.4489,'longitude':-70.6693,
        },format='json')
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.data['latitude'],-33.4489)
        self.assertNotIn('latitude',self.client.get('/api/v1/requests/').data['results'][0])
        self.client.force_authenticate(self.profiles[1].user)
        self.assertEqual(self.client.get(f"/api/v1/requests/{response.data['id']}/").status_code,404)

    def test_haversine_known_distance(self):
        self.assertAlmostEqual(distance_km(0,0,0,1),111.195,places=2)
        self.assertEqual(distance_km(-33.45,-70.67,-33.45,-70.67),0)

    def test_map_document_public_without_tokens(self):
        self.client.force_authenticate(None)
        response=self.client.get('/map/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response['Referrer-Policy'],'strict-origin-when-cross-origin')
        self.assertContains(response,'OpenStreetMap')
        self.assertNotContains(response,'Authorization')
