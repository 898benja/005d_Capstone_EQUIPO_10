from unittest.mock import patch
from io import StringIO
from django.core.management import call_command
from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse
from accounts.models import User

class HealthTests(TestCase):
    def test_anonymous_health_checks_real_database(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        # Los campos diagnósticos adicionales no rompen el contrato del móvil.
        payload = response.json()
        self.assertEqual({key: payload[key] for key in ('status', 'service', 'database')},
                         {'status': 'ok', 'service': 'fix-and-go-api', 'database': 'ok'})

    def test_database_failure_returns_503_without_details(self):
        with patch('core.views.connection.cursor', side_effect=DatabaseError('private details')):
            response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private details', response.content.decode())

    def test_health_rejects_mutation(self):
        self.assertEqual(self.client.post(reverse('health')).status_code, 405)

    def test_admin_requires_login(self):
        self.assertEqual(self.client.get('/admin/').status_code, 302)

    def test_custom_user_stores_hashed_password(self):
        user = User.objects.create_user(username='test-user', password='test-pass-123')
        self.assertNotEqual(user.password, 'test-pass-123')
        self.assertTrue(user.check_password('test-pass-123'))


class DemoDataCommandTests(TestCase):
    def test_seed_is_idempotent_and_reset_preserves_unrelated_users(self):
        unrelated = User.objects.create_user(
            username='usuario-real',
            email='usuario-real@example.test',
            password='test-pass-123',
        )
        call_command('seed_demo_data', stdout=StringIO())
        user_count = User.objects.count()

        call_command('seed_demo_data', stdout=StringIO())
        self.assertEqual(User.objects.count(), user_count)

        call_command('seed_demo_data', '--reset', stdout=StringIO())
        self.assertTrue(User.objects.filter(pk=unrelated.pk).exists())
