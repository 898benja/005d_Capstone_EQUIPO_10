"""Pruebas del catálogo público y la búsqueda de prestadores."""

from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import ProviderProfile, User
from .models import Category, Commune


class CatalogTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username='cliente-catalogo',
            email='cliente-catalogo@example.test',
            password='test-pass-123',
        )
        self.provider = User.objects.create_user(
            username='prestador-catalogo',
            email='prestador-catalogo@example.test',
            password='test-pass-123',
            role=User.Role.PROVIDER,
        )
        self.category = Category.objects.first()
        self.commune = Commune.objects.first()
        self.profile = ProviderProfile.objects.create(
            user=self.provider,
            display_name='Prestador de prueba',
            description='Especialista para las pruebas de catálogo.',
            is_active=True,
        )
        self.profile.categories.add(self.category)
        self.profile.communes.add(self.commune)

    def test_public_catalog_uses_paginated_contract(self):
        for route in ['category-list', 'commune-list']:
            with self.subTest(route=route):
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
                self.assertIn('count', response.data)
                self.assertIn('results', response.data)
                self.assertGreater(response.data['count'], 0)

    def test_provider_search_requires_auth_and_filters_coverage(self):
        self.assertEqual(self.client.get(reverse('provider-list')).status_code, 401)

        self.client.force_authenticate(self.client_user)
        response = self.client.get(reverse('provider-list'), {
            'category': self.category.slug,
            'commune': self.commune.slug,
            'search': 'prueba',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.profile.pk)

    def test_inactive_provider_is_not_public(self):
        self.profile.is_active = False
        self.profile.save(update_fields=['is_active'])
        self.client.force_authenticate(self.client_user)
        self.assertEqual(
            self.client.get(reverse('provider-list')).data['count'],
            0,
        )
        self.assertEqual(
            self.client.get(reverse('provider-detail', args=[self.profile.pk])).status_code,
            404,
        )
