"""User permissions."""

# REST Framework
from rest_framework import permissions


class HasAccountVerified(permissions.BasePermission):
    """Verifies that the request user's account is verified."""

    def has_permission(self, request, view):
        if request.user.is_verified:
            return True
        return False
