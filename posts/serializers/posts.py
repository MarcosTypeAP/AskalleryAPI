"""Post serializers."""

# REST Framework
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

# Django
from django.conf import settings

# Models
from posts.models import Post

# Serializers
from users.serializers import MinimumUserFieldsModelSerializer

# Utils
from utils.serializers import is_asuka_picture, compress_image


class PostModelSerializer(serializers.ModelSerializer):
    """Post model Serializer."""

    user = MinimumUserFieldsModelSerializer(read_only=True)

    class Meta:
        """Meta options."""
        model = Post
        fields = (
            'pk', 'user', 'caption', 'image', 'likes_quantity',
            'comments_quantity', 'created'
        )
        read_only_fields = (
            'pk', 'user', 'image', 'likes_quantity',
            'comments_quantity', 'created'
        )


class PostCreationModelSerializer(serializers.ModelSerializer):
    """Post creation model serializer."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        """Meta options."""
        model = Post
        fields = ('user', 'caption', 'image')

    def validate(self, data):
        import pdb; pdb.set_trace()
        if settings.LOCAL_DEV:
            return data
        if is_asuka_picture(image=data['image'], user=data['user']):
            return data
        raise serializers.ValidationError(
            {'image': 'The image must be about ´Asuka Langley´ ' +
             'from ´Neon Genesis Evangelion´.'}
        )

    def create(self, data):
        """Compress the image of the ´image´ field."""
        data['image'] = compress_image(data['image'])
        return super(PostCreationModelSerializer, self).create(data)


class PostLikeSerializer(serializers.Serializer):
    """Post like serializer."""

    pk = serializers.IntegerField()

    request_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_pk(self, value):
        """Verifies the liked post exists."""
        liked_post = get_object_or_404(Post, pk=value, is_active=True)
        self.context['liked_post'] = liked_post
        return value

    def create(self, data):
        """Establishes a relationship between
        the request user and the liked post.
        """
        request_user = data['request_user']
        liked_post = self.context['liked_post']
        if self.context['request'].method == 'POST':
            liked_post.add_like(request_user)
        else:
            liked_post.remove_like(request_user)
        return liked_post
