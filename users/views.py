"""User views."""

# REST Framework
from rest_framework import viewsets, status
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
)

# Models
from users.models import User


class UserViewSet(viewsets.GenericViewSet):
    """User view set.
    
    Handles sign up, login, account verification
    and profile update.
    """

    def get_permissions(self):
        """Assign permissions based on action."""
        if self.action in ['signup']:
            permissions = [AllowAny]
        elif self.action in ['follow']:
            permissions = [IsAuthenticated]
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
