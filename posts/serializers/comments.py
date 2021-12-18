"""Comment Serializers."""

# REST Framework
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

# Models
from posts.models import Post, Comment

# Serializers
from users.serializers import MinimumUserFieldsModelSerializer


class CommentModelSerializer(serializers.ModelSerializer):
    """Comment Model Serializer."""

    user = MinimumUserFieldsModelSerializer(read_only=True)

    request_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
        write_only=True
    )

    class Meta:
        """Meta options."""
        model = Comment
        fields = ('pk', 'user', 'content', 'request_user', 'post')
        read_only_fields = ('pk', 'user')

    def to_internal_value(self, data):
        if 'post' in data:
            get_object_or_404(Post, pk=data['post'], is_active=True)
        return super(CommentModelSerializer, self).to_internal_value(data)

    def create(self, data):
        """Creates a new comment and establishes a relationship
        between it and the passed post´.
        """
        comment = data['post'].add_comment(
            user=data['request_user'], content=data['content']
        )
        return comment


class CommentLikeSerializer(serializers.Serializer):
    """Comment like serializer."""

    pk = serializers.IntegerField()

    request_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_pk(self, value):
        """Verifies the liked comment exists."""
        liked_comment = get_object_or_404(
            Comment, pk=value, post__is_active=True
        )
        self.context['liked_comment'] = liked_comment
        return value

    def create(self, data):
        """Establishes a relationship between
        the request user and the liked comment.
        """
        request_user = data['request_user']
        liked_comment = self.context['liked_comment']
        if self.context['request'].method == 'POST':
            liked_comment.add_like(request_user)
        else:
            liked_comment.remove_like(request_user)
        return liked_comment
