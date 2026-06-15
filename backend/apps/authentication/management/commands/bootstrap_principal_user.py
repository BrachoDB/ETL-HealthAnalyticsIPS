from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.authentication.models import User


class Command(BaseCommand):
    help = "Crea automáticamente el usuario principal/superusuario si no existe"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default=getattr(settings, 'BOOTSTRAP_ADMIN_USERNAME', 'admin'))
        parser.add_argument('--email', type=str, default=getattr(settings, 'BOOTSTRAP_ADMIN_EMAIL', 'admin@example.com'))
        parser.add_argument('--password', type=str, default=getattr(settings, 'BOOTSTRAP_ADMIN_PASSWORD', 'admin123'))
        parser.add_argument('--role', type=str, default=getattr(settings, 'BOOTSTRAP_ADMIN_ROLE', 'ADMIN'))

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        role = options['role']

        user, created = User.objects.get_or_create(username=username, defaults={
            'email': email,
            'role': role,
        })

        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            # Asegura también role ADMIN si aplica (por seguridad)
            if hasattr(User, 'ADMIN'):
                user.role = User.ADMIN
            group, _ = Group.objects.get_or_create(name=user.role)
            user.groups.add(group)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Bootstrap: creado superusuario {username}'))
        else:
            # Si existe pero no es superuser, lo normalizamos
            updated = False
            if not user.is_staff:
                user.is_staff = True
                updated = True
            if not user.is_superuser:
                user.is_superuser = True
                updated = True
            if role and user.role != role and hasattr(User, 'ADMIN'):
                # solo intenta ajustar si el rol viene explícito
                user.role = role
                updated = True
            if updated:
                group, _ = Group.objects.get_or_create(name=user.role)
                user.groups.add(group)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Bootstrap: actualizado permisos para {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'Bootstrap: el usuario {username} ya existe y ya tiene permisos'))

