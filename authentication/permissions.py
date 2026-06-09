from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    required_roles = set()

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = getattr(getattr(user, 'profile', None), 'role', None)
        return role in self.required_roles


class IsAdmin(RolePermission):
    required_roles = {'ADMIN'}


class IsMedico(RolePermission):
    required_roles = {'MEDICO'}


class IsAnalista(RolePermission):
    required_roles = {'ANALISTA'}

