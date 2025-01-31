from rest_framework import permissions


class IsHimself(permissions.BasePermission):
    """ Checks if user is himself """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsHimselfOrReadOnly(permissions.BasePermission):
    """ Checks if user is the owner of  """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
