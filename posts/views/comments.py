"""Comment views."""

# REST Framework
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import (
    IsAuthenticated
)
from posts.permissions import IsCommentOrPostOwner

# Serializers
from posts.serializers import (
    CommentModelSerializer,
)

# Models
from posts.models import Comment, Post


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Comment view set."""

    serializer_class = CommentModelSerializer

    queryset = Comment.objects.all()

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated]
        if self.action == "destroy":
            permissions.append(IsCommentOrPostOwner)
        return [p() for p in permissions]

    def perform_destroy(self, instance):
        """Deletes the given comment from
        the post method.
        """
        post = Post.objects.get(pk=instance.post.pk)
        post.remove_comment(comment=instance.pk)
