"""Post views."""

# REST Framework
from rest_framework import viewsets, mixins, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

# Django
from django.http import FileResponse, Http404

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from posts.permissions import IsPostOwner

# Serializers
from posts.serializers import (
    PostCreationModelSerializer, PostModelSerializer, PostLikeSerializer,
    CommentModelSerializer
)
from users.permissions import HasAccountVerified

# Models
from posts.models import Post, Comment

# Utils
from os import remove as remove_file
from os.path import exists as file_exists


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
        permissions = [IsAuthenticated, HasAccountVerified]
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
        elif self.action == 'comments':
            post = get_object_or_404(
                Post, pk=self.kwargs.get('pk'), is_active=True
            )
            queryset = Comment.objects.filter(post=post)
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
        elif self.action == 'comments':
            return CommentModelSerializer

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

    @action(detail=True, methods=['GET'])
    def comments(self, request, *args, **kwargs):
        """List all comments of the given post."""
        return self.list(request, *args, **kwargs)


def serve_temporal_image(response, *args, **kwargs):
    """Serves a temporal image if this is in /app/tmp_images/"""
    image_path = '/app/tmp_images/{}'.format(kwargs.get('image'))
    if file_exists(image_path):
        with open(image_path, 'rb') as img:
            response = FileResponse(img)
        remove_file(image_path)
        return response
    else:
        raise Http404('Image not found')
