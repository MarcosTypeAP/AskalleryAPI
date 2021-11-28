"""User views."""

# REST Framework
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)

# Serializers
from users.serializers import (
    UserModelSerializer,
    UserSignUpSerializer,
    FollowSerializer,
    ProfileModelSerializer
)

# Models
from users.models import User


class UserViewSet(viewsets.GenericViewSet):
    """User view set.

    Handles sign up, login, account verification
    and profile update.
    """

    queryset = User.objects.filter(is_client=True)

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated]
        if self.action == 'signup':
            permissions = [AllowAny]
        return [p() for p in permissions]

    @action(detail=False, methods=['POST'])
    def signup(self, request):
        """User sign up."""
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data
        return Response(data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST', 'DELETE'])
    def follow(self, request, *args, **kwargs):
        """Establishes or removes a follow relationship
        between the request user and the given user.
        """
        serializer = FollowSerializer(
            data=kwargs, context={
                'request': request,
                'method': request.method
            }
        )
        serializer.is_valid(raise_exception=True)
        followed_user = serializer.save()
        data = {
            'current_user': request.user.pk,
            'followed_user': followed_user.pk,
        }
        if request.method == 'DELETE':
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data, status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['PATCH'])
    def profile(self, request, *args, **kwargs):
        """Realizes partial updates to
        the request user's profile.'
        """
        serializer = ProfileModelSerializer(
            request.user.profile,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

