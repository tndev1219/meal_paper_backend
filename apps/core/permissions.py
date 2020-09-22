from rest_framework import permissions


class BasePermission(permissions.BasePermission):
    def _is_admin(self, request):
        return request.user.is_authenticated() and request.user.is_staff


class IsAdminOrSafeMethod(BasePermission):
    """
    Permission check for admin or access for safe methods
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated() and request.user.role == 'admin'


class IsAdmin(BasePermission):
    """
    Permission check for admin
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated() and request.user.role == 'admin'


class IsPropertyManager(BasePermission):
    """
    Permission check for admin
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'property_manager')


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated() and obj.advert.user == request.user
