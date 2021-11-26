"""Post permissions."""

# REST Framework
from rest_framework import permissions


class IsCommentOrPostOwner(permissions.BasePermission):
    """Allows access only to the comment or post owner."""

    def has_object_permission(self, request, view, obj):
        """Allows access only to the request user who is the
        comment or post owner.
        """
        return request.user == obj.user or request.user == obj.post.user
