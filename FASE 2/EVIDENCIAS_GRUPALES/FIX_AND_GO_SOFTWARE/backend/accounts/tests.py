"""Contrato de identidad con datos ficticios y base aislada."""
from datetime import timedelta
from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from catalog.models import Category, Commune
from .models import ProviderProfile, User


class IdentityTests(APITestCase):
    def payload(self):
        return dict(email='cliente@example.test', password='Mvp!demo-X94-tree',
                    first_name='Demo', last_name='Prueba', role='CLIENT')

    def register(self, data=None):
        return self.client.post(reverse('register'), data or self.payload(), format='json')

    def test_client_registration_hashes_password(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        user = User.objects.get()
        self.assertTrue(user.check_password(self.payload()['password']))
        self.assertNotEqual(user.password, self.payload()['password'])
        self.assertNotIn('password', response.data['user'])
        self.assertFalse(ProviderProfile.objects.exists())

    def test_provider_registration_creates_profile(self):
        data = self.payload()
        data.update(role='PROVIDER', display_name='Prestador demo')
        self.assertEqual(self.register(data).status_code, 201)
        self.assertEqual(ProviderProfile.objects.get().display_name, 'Prestador demo')

    def test_registration_rolls_back_when_token_creation_fails(self):
        with patch('accounts.serializers.Token.objects.create', side_effect=RuntimeError('test')):
            response = self.register()
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.data['code'], 'server_error')
            self.assertNotIn('RuntimeError', str(response.data))
        self.assertFalse(User.objects.exists())

    def test_case_insensitive_duplicate_is_rejected(self):
        self.register()
        data = self.payload()
        data['email'] = 'CLIENTE@EXAMPLE.TEST'
        self.assertEqual(self.register(data).status_code, 400)
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_registration(self):
        for change in [{'password': '12345678'}, {'role': 'ADMIN'}, {'role': 'PROVIDER'}]:
            with self.subTest(change=change):
                data = self.payload()
                data.update(change)
                self.assertEqual(self.register(data).status_code, 400)
        self.assertFalse(User.objects.exists())

    def test_login_me_logout_revokes_token(self):
        self.register()
        response = self.client.post(reverse('login'), {
            'email': 'CLIENTE@EXAMPLE.TEST', 'password': self.payload()['password'],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])
        self.assertEqual(self.client.get(reverse('me')).status_code, 200)
        self.assertEqual(self.client.post(reverse('logout')).status_code, 200)
        self.assertEqual(self.client.get(reverse('me')).status_code, 401)

    def test_invalid_and_inactive_login(self):
        self.register()
        for active, password in [(True, 'wrong'), (False, self.payload()['password'])]:
            User.objects.update(is_active=active)
            self.assertEqual(self.client.post(reverse('login'), {
                'email': self.payload()['email'], 'password': password,
            }).status_code, 400)

    def test_anonymous_and_invalid_token(self):
        self.assertEqual(self.client.get(reverse('me')).status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid')
        self.assertEqual(self.client.get(reverse('me')).status_code, 401)

    def test_expired_token_is_rejected_and_deleted(self):
        self.register()
        token = Token.objects.get()
        Token.objects.filter(pk=token.pk).update(
            created=timezone.now() - timedelta(hours=25),
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(self.client.get(reverse('me')).status_code, 401)
        self.assertFalse(Token.objects.filter(pk=token.pk).exists())

    def test_login_rotates_expired_token(self):
        self.register()
        previous = Token.objects.get()
        Token.objects.filter(pk=previous.pk).update(
            created=timezone.now() - timedelta(hours=25),
        )
        response = self.client.post(reverse('login'), {
            'email': self.payload()['email'],
            'password': self.payload()['password'],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['token'], previous.key)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])
        self.assertEqual(self.client.get(reverse('me')).status_code, 200)

    def test_client_cannot_edit_provider_profile(self):
        self.register()
        self.client.force_authenticate(User.objects.get())
        self.assertEqual(self.client.patch(reverse('provider-profile'), {
            'display_name': 'Changed',
        }).status_code, 403)

    def test_provider_can_update_own_profile(self):
        data = self.payload()
        data.update(role='PROVIDER', display_name='Prestador inicial')
        self.assertEqual(self.register(data).status_code, 201)
        provider = User.objects.get()
        category = Category.objects.first()
        commune = Commune.objects.first()
        self.client.force_authenticate(provider)
        response = self.client.patch(reverse('provider-profile'), {
            'display_name': 'Prestador actualizado',
            'years_experience': 4,
            'categories': [category.pk],
            'communes': [commune.pk],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['display_name'], 'Prestador actualizado')
        self.assertEqual(response.data['categories'][0]['id'], category.pk)
        self.assertEqual(response.data['communes'][0]['id'], commune.pk)

    def test_registration_saves_reusable_personal_data(self):
        data = self.payload()
        data.update(phone='+56900000000', default_address='Dirección ficticia', default_commune=Commune.objects.first().pk)
        response = self.register(data)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['user']['default_address'], data['default_address'])
        self.assertEqual(User.objects.get().default_commune_id, data['default_commune'])

    def test_registration_rejects_invalid_phone_and_too_long_email(self):
        data = self.payload(); data['phone'] = '--------'
        self.assertEqual(self.register(data).status_code, 400)
        data = self.payload(); data['email'] = 'x' * 140 + '@example.test'
        self.assertEqual(self.register(data).status_code, 400)
