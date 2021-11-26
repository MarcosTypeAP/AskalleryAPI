"""Profile serializers."""

# REST Framework
from enum import unique
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Models
from users.models import Profile, User


class ProfileModelSerializer(serializers.ModelSerializer):
    """Profile model serializer."""
    class Meta:
        """Meta options."""
        model = Profile
        fields = (
            'picture',
            'biography',
            'followers_quantity',
            'following_quantity',
        )
        read_only_fields = (
            'following_quantity',
            'followers_quantity',
        )


class FollowSerializer(serializers.Serializer):
    """Follow serializer.
    
    Validates if the given user exists and 
    establishes a relationship between it
    and the request user.
    """

    pk = serializers.IntegerField()

    request_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        """Verify the followed user exists
        and it's not the request user.
        """
        try:
            followed_user = User.objects.get(pk=data['pk'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid user.")

        if followed_user == data['request_user']:
            raise serializers.ValidationError("An user cannot follow itself.")

        self.context['followed_user'] = followed_user

        return data

    def create(self, data):
        """Establishes a relationship between
        the request user and the followed user.
        """
        request_user = data['request_user']
        followed_user = self.context['followed_user']

        if self.context['method'] == 'POST':
            request_user.profile.start_follow(followed_user)
        else:
            request_user.profile.stop_following(followed_user)

        return followed_user
