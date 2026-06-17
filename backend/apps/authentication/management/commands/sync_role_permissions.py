from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.analytics.models import ExportAudit
from apps.etl.models import Patient
from apps.ml.models import MLModelMetrics


ROLE_PERMISSIONS = {
    'ADMIN': {
        Patient: [
            ('view_patient', 'Puede consultar pacientes del ETL'),
            ('change_patient', 'Puede modificar pacientes del ETL'),
            ('add_patient', 'Puede crear pacientes del ETL'),
            ('delete_patient', 'Puede eliminar pacientes del ETL'),
            ('view_etllog', 'Puede consultar logs del ETL'),
            ('run_etl', 'Puede ejecutar procesos ETL'),
            ('upload_etl', 'Puede cargar archivos ETL'),
        ],
        ExportAudit: [
            ('view_kpi', 'Puede consultar indicadores analíticos'),
            ('export_analytics', 'Puede exportar datos analíticos'),
        ],
        MLModelMetrics: [
            ('predict_ml', 'Puede ejecutar predicciones ML'),
        ],
    },
    'MEDICO': {
        Patient: [
            ('view_patient', 'Puede consultar pacientes del ETL'),
            ('change_patient', 'Puede modificar pacientes del ETL'),
            ('add_patient', 'Puede crear pacientes del ETL'),
            ('delete_patient', 'Puede eliminar pacientes del ETL'),
            ('view_etllog', 'Puede consultar logs del ETL'),
            ('run_etl', 'Puede ejecutar procesos ETL'),
            ('upload_etl', 'Puede cargar archivos ETL'),
        ],
        ExportAudit: [
            ('view_kpi', 'Puede consultar indicadores analíticos'),
            ('export_analytics', 'Puede exportar datos analíticos'),
        ],
        MLModelMetrics: [
            ('predict_ml', 'Puede ejecutar predicciones ML'),
        ],
    },
    'ANALISTA': {
        Patient: [
            ('view_patient', 'Puede consultar pacientes del ETL'),
            ('view_etllog', 'Puede consultar logs del ETL'),
        ],
        ExportAudit: [
            ('view_kpi', 'Puede consultar indicadores analíticos'),
            ('export_analytics', 'Puede exportar datos analíticos'),
        ],
    },
}


class Command(BaseCommand):
    help = 'Sincroniza grupos de roles con permisos Django.'

    def handle(self, *args, **options):
        for role, permissions_by_model in ROLE_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(name=role)
            group.permissions.set(self._get_permissions(permissions_by_model))
            self.stdout.write(self.style.SUCCESS(f'Grupo {role} sincronizado con {group.permissions.count()} permisos.'))

        for user in get_user_model().objects.all():
            role = getattr(user, 'role', None)
            if role in ROLE_PERMISSIONS:
                group = Group.objects.get(name=role)
                user.groups.add(group)
                self.stdout.write(self.style.SUCCESS(f'Usuario {user.username} asignado al grupo {role}.'))

    def _get_permissions(self, permissions_by_model):
        permissions = []
        for model, codename_labels in permissions_by_model.items():
            content_type = ContentType.objects.get_for_model(model)
            for codename, label in codename_labels:
                permission, _ = Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={'name': label},
                )
                permissions.append(permission)
        return permissions
