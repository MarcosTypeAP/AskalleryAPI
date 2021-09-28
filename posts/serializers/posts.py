"""Post serializers."""

# REST Framework
from rest_framework import serializers

# Models
from posts.models import Post
from users.models import User

# Serializers
from users.serializers import UserModelSerializer


class PostModelSerializer(serializers.ModelSerializer):
    """Post model Serializer."""

    class UserModelSerializer(serializers.ModelSerializer):
        """Returns some fields for this serializer's user field."""

        class Meta:
            """Meta options."""
            model = User
            fields = ('pk', 'username')

    user = UserModelSerializer()

    class Meta:
        """Meta options."""
        model = Post
        fields = (
            'pk', 'user',
            'caption', 'image',
            'likes_quantity', 
            'comments_quantity'
        )
        read_only_fields = (
            'pk', 'user',
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


