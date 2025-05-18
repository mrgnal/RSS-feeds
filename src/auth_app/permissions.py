from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return str(obj.user_id) == str(request.user.get('id'))

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'is_superuser') and request.user.is_superuser