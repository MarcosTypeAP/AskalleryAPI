"""Comment views."""

# REST Framework
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import (
    IsAuthenticated
)
from posts.permissions import IsCommentOrPostOwner

# Serializers
from posts.serializers import (
    CommentModelSerializer,
    CommentLikeSerializer
)

# Models
from posts.models import Comment, Post


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Comment view set."""

    queryset = Comment.objects.filter(post__is_active=True)

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated]
        if self.action == "destroy":
            permissions.append(IsCommentOrPostOwner)
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Assigns serializer class based on action."""
        serializer_class = CommentModelSerializer
        if self.action == "like":
            serializer_class = CommentLikeSerializer
        return serializer_class

    def perform_destroy(self, instance):
        """Deletes the given comment from
        the post method.
        """
        post = Post.objects.get(pk=instance.post.pk)
        post.remove_comment(comment=instance.pk)

    @action(detail=True, methods=['POST', 'DELETE'])
    def like(self, request, *args, **kwargs):
        """Establishes or removes a relationship
        between the request user and the given comment.
        """
        serializer = self.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        liked_comment = serializer.save()
        if request.method == "DELETE":
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {'liked_comment': liked_comment.pk}
        return Response(data, status.HTTP_201_CREATED)
