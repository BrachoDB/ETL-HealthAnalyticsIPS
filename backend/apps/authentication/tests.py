from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.authentication.models import User


class AuthenticationSecurityTest(TestCase):
    def test_open_registration_is_closed_by_default(self):
        client = APIClient()
        response = client.post('/api/auth/register/', {
            'username': 'nuevo',
            'password': 'password123',
            'email': 'nuevo@example.com',
        }, format='json')

        self.assertEqual(response.status_code, 401)

    def test_sync_role_permissions_assigns_groups(self):
        user = User.objects.create_user(username='analista-permisos', password='password123', role='ANALISTA')

        call_command('sync_role_permissions')
        user.refresh_from_db()

        self.assertTrue(user.groups.filter(name='ANALISTA').exists())
        self.assertTrue(user.has_perm('analytics.export_analytics'))
        self.assertFalse(user.has_perm('ml.predict_ml'))
        self.assertTrue(Group.objects.filter(name='MEDICO').exists())
