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
from posts.permissions import IsCommentOrPostOwner

# Serializers
from posts.serializers import (
    PostCreationModelSerializer,
    PostModelSerializer,
    LikeSerializer,
    CreateCommentSerializer,
    DeleteCommentSerializer,
)

# Models
from posts.models import Post, Comment
from users.models import User


class PostViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Post view set."""

    queryset = Post.objects.all()

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated]
        if self.action in ("retrieve", "list"):
            permissions = [AllowAny]
        elif self.action == 'comment':
            permissions.append(IsCommentOrPostOwner)
        return [p() for p in permissions]

    def get_serializer_class(self):
        """Assigns serializer based on action."""
        if self.action == 'create':
            return PostCreationModelSerializer
        elif self.action in ('list', "retrieve"):
            return PostModelSerializer
        elif self.action == 'like':
            return LikeSerializer

    def get_object(self, *args, **kwargs):
        """Returns a ´Comment´ instance by using
        ´pk´ based on action and method.
        """
        if self.action == 'comment' and self.request.method == 'DELETE':
            obj = get_object_or_404(Comment, pk=kwargs['comment_pk'])
            self.check_object_permissions(self.request, obj)
            return obj
        return super(PostViewSet, self).get_object(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        get_object_or_404(User, pk=kwargs.get("pk"))
        queryset = Post.objects.filter(user__pk=kwargs["pk"])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST', 'DELETE'])
    def like(self, request, *args, **kwargs):
        """Establishes or removes a relationship
        between the request user and the given post.
        """
        serializer = self.get_serializer(
            data={'post_pk': kwargs['pk']},
            context={
                "request": request,
                "method": request.method
            }
        )
        serializer.is_valid(raise_exception=True)
        liked_post = serializer.save()
        if request.method == "DELETE":
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {'liked_post': liked_post.pk}
        return Response(data, status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST', 'DELETE'])
    def comment(self, request, *args, **kwargs):
        if request.method == "POST":
            serializer = CreateCommentSerializer(
                data=request.data, context={'request': request}
            )
        else:
            self.get_object(**kwargs)
            serializer = DeleteCommentSerializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        commented_post = serializer.save()
        if request.method == 'DELETE':
            return Response(status=status.HTTP_204_NO_CONTENT)
        data = {
            'commented_post': commented_post.pk,
            'comment_content': serializer.data['content']
        }
        return Response(data, status=status.HTTP_201_CREATED)
