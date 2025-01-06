

from rest_framework.permissions import BasePermission

class IsAdminOrStaff(BasePermission):
    """
    Allows access only to admin or staff users.
    """
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_admin)
