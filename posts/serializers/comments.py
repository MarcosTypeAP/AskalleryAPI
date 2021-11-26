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

    class Meta:
        """Meta options."""
        model = Comment
        fields = ('pk', 'user', 'content')
        read_only_fields = ('pk', 'user')


class CreateCommentSerializer(serializers.Serializer):
    """Create comment serializer."""

    request_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    post_pk = serializers.IntegerField()

    content = serializers.CharField(min_length=1, max_length=500)

    def validate_post_pk(self, data):
        """Validates the given post exists."""
        commented_post = get_object_or_404(Post, pk=data)
        self.context['commented_post'] = commented_post
        return data

    def create(self, data):
        """Creates a new comment and establishes a relationship
        between it and the passed post´.
        """
        commented_post = self.context['commented_post']
        commented_post.add_comment(
            user=data['request_user'], content=data['content']
        )
        return commented_post

    def save(self, **kwargs):
        """Removes ´self.instance´ because when ´serializer.data´
        is accessed from this serializer instance, it raises an error.
        """
        validated_data = {**self.validated_data, **kwargs}
        return self.create(validated_data)


class DeleteCommentSerializer(serializers.Serializer):
    """Delete comment serializer."""

    post_pk = serializers.IntegerField()

    comment_pk = serializers.IntegerField()

    def validate_post_pk(self, data):
        """Validates the given post exists."""
        commented_post = get_object_or_404(Post, pk=data)
        self.context['commented_post'] = commented_post
        return data

    def validate_comment_pk(self, data):
        """Validates the given comment exists."""
        get_object_or_404(Comment, pk=data)
        return data

    def create(self, data):
        """Deletes the given comment."""
        commented_post = self.context['commented_post']
        commented_post.remove_comment(comment=data['comment_pk'])
        return commented_post
