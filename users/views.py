"""User views."""

# REST Framework
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

# Filters
from users.filters import CustomSearchFilter

# Renderers
from rest_framework.renderers import (JSONRenderer, TemplateHTMLRenderer)

# Permissions
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from users.permissions import HasAccountVerified

# Serializers
from users.serializers import (
    UserModelSerializer, UserSignUpModelSerializer, ProfileFollowSerializer,
    ProfileModelSerializer, MinimumUserFieldsModelSerializer,
    AccountVerificationSerializer
)
from posts.serializers import PostModelSerializer

# Models
from users.models import User
from posts.models import Post


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """User view set."""

    filter_backends = [CustomSearchFilter]

    def get_permissions(self):
        """Assign permissions based on action."""
        permissions = [IsAuthenticated, HasAccountVerified]
        if self.action in [
            'signup', 'verify', 'list', 'posts', 'retrieve'
        ]:
            permissions = [AllowAny]
        return [p() for p in permissions]

    def get_queryset(self):
        """Assigns queryset based on action."""
        queryset = User.objects.filter(is_client=True, is_verified=True)
        if self.action == 'followers':
            user = get_object_or_404(
                User,
                pk=self.kwargs.get('pk'),
                is_client=True,
                is_verified=True
            )
            queryset = user.profile.followers.all()
        elif self.action == 'following':
            user = get_object_or_404(
                User,
                pk=self.kwargs.get('pk'),
                is_client=True,
                is_verified=True
            )
            queryset = user.profile.following.all()
        elif self.action == 'posts':
            user = get_object_or_404(User, pk=self.kwargs.get('pk'))
            queryset = Post.objects.filter(user=user, is_active=True)
        return queryset

    def get_serializer_class(self):
        """Assigns serializer based on action."""
        if self.action in ['list', 'followers', 'following']:
            serializer = MinimumUserFieldsModelSerializer
        if self.action == 'retrieve':
            serializer = UserModelSerializer
        if self.action == 'posts':
            serializer = PostModelSerializer
        if self.action == 'signup':
            serializer = UserSignUpModelSerializer
        if self.action == 'verify':
            serializer = AccountVerificationSerializer
        if self.action == 'follow':
            serializer = ProfileFollowSerializer
        if self.action == 'profile':
            serializer = ProfileModelSerializer
        return serializer

    def get_renderers(self):
        """Assigns renderers based on action."""
        renderers = [JSONRenderer]
        if self.action == 'verify':
            renderers.append(TemplateHTMLRenderer)
        return [r() for r in renderers]

    @action(detail=False, methods=['POST'])
    def signup(self, request):
        """User sign up."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        return Response(data, status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'])
    def verify(self, request, *args, **kwargs):
        """Account verification."""
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {'message': 'Account verified.'}
        return Response(
            data=data,
            status=status.HTTP_200_OK,
            template_name='users/account_verified.html',
        )

    @action(detail=True, methods=['POST', 'DELETE'])
    def follow(self, request, *args, **kwargs):
        """Establishes or removes a follow relationship
        between the request user and the given user.
        """
        serializer = self.get_serializer(
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
        serializer = self.get_serializer(
            request.user.profile, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['GET'])
    def followers(self, request, *args, **kwargs):
        """Lists all followers of the request user."""
        return self.list(request, *args, **kwargs)

    @action(detail=True, methods=['GET'])
    def following(self, request, *args, **kwargs):
        """Lists all followers of the request user."""
        return self.list(request, *args, **kwargs)

    @action(detail=True, methods=['GET'])
    def posts(self, request, *args, **kwargs):
        """List all post of the request user."""
        return self.list(request, *args, **kwargs)
