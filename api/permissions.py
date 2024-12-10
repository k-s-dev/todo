from rest_framework import permissions


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only owner or admin to create, view or edit objects.
    """
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.is_superuser
