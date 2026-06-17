from rest_framework import permissions

from apps.authentication.models import User


ROLE_ADMIN = User.ADMIN
ROLE_MEDICO = User.MEDICO
ROLE_ANALISTA = User.ANALISTA


def has_any_permission(user, permission_pairs):
    return any(user.has_perm(f'{app_label}.{codename}') for app_label, codename in permission_pairs)


def has_any_role(user, roles):
    return user and user.is_authenticated and getattr(user, 'role', None) in roles


def has_role_or_permission(user, roles, permission_pairs):
    return user and user.is_authenticated and (user.is_superuser or has_any_role(user, roles) or has_any_permission(user, permission_pairs))


class IsAdminOrMedico(permissions.BasePermission):
    allowed_roles = {ROLE_ADMIN, ROLE_MEDICO}
    permission_pairs = [
        ('etl', 'run_etl'),
        ('etl', 'upload_etl'),
        ('etl', 'change_patient'),
        ('etl', 'add_patient'),
        ('etl', 'delete_patient'),
        ('ml', 'predict_ml'),
    ]

    def has_permission(self, request, view):
        return has_role_or_permission(request.user, self.allowed_roles, self.permission_pairs)


class IsReadOnlyClinicalRole(permissions.BasePermission):
    allowed_roles = {ROLE_ADMIN, ROLE_MEDICO, ROLE_ANALISTA}
    permission_pairs = [
        ('etl', 'view_patient'),
        ('etl', 'view_etllog'),
        ('analytics', 'view_kpi'),
    ]

    def has_permission(self, request, view):
        return has_role_or_permission(request.user, self.allowed_roles, self.permission_pairs)

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or self.has_permission(request, view)


class CanExportAnalytics(permissions.BasePermission):
    allowed_roles = {ROLE_ADMIN, ROLE_MEDICO, ROLE_ANALISTA}
    permission_pairs = [('analytics', 'export_analytics')]

    def has_permission(self, request, view):
        return has_role_or_permission(request.user, self.allowed_roles, self.permission_pairs)
