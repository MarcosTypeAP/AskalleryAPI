"""Post views."""

# REST Framework
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

# Serializers
from posts.serializers import (
    PostCreationModelSerializer,
    PostModelSerializer,
)

# Models
from posts.models import Post
from users.models import User


class PostViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet,):
    """Post view set."""

    queryset = Post.objects.all()

    def get_permissions(self):
        """Assign permissions based on action."""
        print(self.action)
        if self.action in ('destroy', 'create'):
            permissions = [IsAuthenticated]
        elif self.action in ('retrieve', 'list'):
            permissions = [AllowAny]
        else:
            permissions = [IsAuthenticated]
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Assigns serializers based on action."""
        if self.action == 'create':
            return PostCreationModelSerializer
        elif self.action in ('list', 'retrieve'):
            return PostModelSerializer

    def retrieve(self, request, *args, **kwargs):
        get_object_or_404(User, pk=kwargs.get('pk'))
        queryset = Post.objects.filter(user__pk=kwargs['pk'])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)