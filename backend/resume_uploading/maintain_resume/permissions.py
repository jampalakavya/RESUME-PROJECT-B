from rest_framework.permissions import BasePermission

class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        # Only superusers can access admin dashboard APIs
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )