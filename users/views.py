"""User views."""

# REST Framework
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
# from users.permissions import IsAccountOwner

# Serializers
from users.serializers import (
    UserModelSerializer,
    UserSignUpSerializer,
    FollowSerializer,
)

# Models
from users.models import User


class UserViewSet(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
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

    @action(detail=False, methods=['POST', 'DELETE'])
    def follow(self, request):
        """Establishes or removes a relationship
        between this user and the given user.
        """
        serializer = FollowSerializer(
            data=request.query_params, 
            context={
                'request':request,
                'method': self.request.method,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'current_user': self.request.user.email,
            'followed_user': request.query_params['user_email'],
        }
        if self.request.method == 'DELETE':
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(data, status.HTTP_201_CREATED)