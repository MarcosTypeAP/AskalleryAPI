"""Post serializers."""

# REST Framework
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

# Models
from posts.models import Post

# Serializers
from users.serializers import MinimumUserFieldsModelSerializer


class PostModelSerializer(serializers.ModelSerializer):
    """Post model Serializer."""

    user = MinimumUserFieldsModelSerializer(read_only=True)

    class Meta:
        """Meta options."""
        model = Post
        fields = (
            'pk', 'user', 'caption', 'image', 'likes_quantity',
            'comments_quantity'
        )
        read_only_fields = (
            'pk',
            'user',
            'likes_quantity',
            'comments_quantity',
        )


class PostCreationModelSerializer(serializers.ModelSerializer):
    """Post creation model serializer."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        """Meta options."""
        model = Post
        fields = ('user', 'caption', 'image')


class LikeSerializer(serializers.Serializer):
    """Like serializer."""

    post_pk = serializers.IntegerField()

    request_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_post_pk(self, data):
        """Verifies the liked post exists."""
        liked_post = get_object_or_404(Post, pk=data)
        self.context['liked_post'] = liked_post

        return data

    def create(self, data):
        """Establishes a relationship between
        the request user and the liked post.
        """
        request_user = data['request_user']
        liked_post = self.context['liked_post']

        if self.context['method'] == 'POST':
            liked_post.add_like(request_user)
        else:
            liked_post.remove_like(request_user)

        return liked_post
