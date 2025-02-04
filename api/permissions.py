from rest_framework import permissions


class IsHimself(permissions.BasePermission):
    """ Checks if user is himself """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Allows unsafe methods (POST, PUT, PATCH, DELETE) only for staff users.
    Others can only read (GET).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Allows editing of the object only by its owner.
    The owner, moderators, or is_staff can view it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user or request.user.is_staff
        return obj.user == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to moderators (is_staff).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
