"""Post views."""

# REST Framework
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from posts.permissions import IsPostOwner

# Serializers
from posts.serializers import (
    PostCreationModelSerializer, PostModelSerializer, PostLikeSerializer
)

# Models
from posts.models import Post
from users.models import User


class PostViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Post view set."""

    filter_backends = [OrderingFilter]
    ordering_fields = ['created', 'modified']
    ordering = ['-created']

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated]
        if self.action == 'retrieve':
            permissions = [AllowAny]
        if self.action in ['update', 'partial_update', 'destroy']:
            permissions.append(IsPostOwner)
        return [p() for p in permissions]

    def get_queryset(self):
        """Assigns queryset based on action."""
        queryset = Post.objects.filter(is_active=True)
        if self.action == 'liked':
            queryset = Post.objects.filter(
                likes=self.request.user, is_active=True
            )
        return queryset

    def get_serializer_class(self):
        """Assigns serializer based on action."""
        if self.action in (
            'liked', 'list', 'retrieve', 'partial_update', 'update'
        ):
            return PostModelSerializer
        elif self.action == 'create':
            return PostCreationModelSerializer
        elif self.action == 'like':
            return PostLikeSerializer

    def perform_destroy(self, instance):
        """Changes the instance's 'is_active' attribute to 'False'
        instead of deleting the instance.
        """
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['POST', 'DELETE'])
    def like(self, request, *args, **kwargs):
        """Establishes or removes a relationship
        between the request user and the given post.
        """
        serializer = self.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        liked_post = serializer.save()
        if request.method == "DELETE":
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {'liked_post': liked_post.pk}
        return Response(data, status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def liked(self, request, *args, **kwargs):
        """List all liked posts by the request user."""
        return self.list(request, *args, **kwargs)
