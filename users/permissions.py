"""User permissions."""

# REST Framework
from rest_framework import permissions


class IsAccountOwner(permissions.BasePermission):
    """Verify if the user is owner of the account."""

    def has_object_permission(self, request, view, obj):
        print(obj)
        if self.request.user != obj:
            return False
        return True