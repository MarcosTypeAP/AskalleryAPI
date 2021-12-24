"""Profile serializers."""

# REST Framework
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

# Models
from users.models import Profile, User

# Utils
from utils.serializers import size_reduction


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

    def validate_picture(self, value):
        """Verifies the image format and that is an asuka picture.."""
        VALID_IMAGE_EXTENSIONS = ('JPG', 'JPEG', 'PNG')
        if value.image.format not in VALID_IMAGE_EXTENSIONS:
            raise serializers.ValidationError(
                {'image': 'Only jpg, jpeg and png formats are allowed.'}
            )
        return value

    def update(self, instance, data):
        """Compress and resize `picture`."""
        data['picture'] = size_reduction(
            data['picture'], quality=60,
            width=600, height=600
        )
        return super(ProfileModelSerializer, self).update(instance, data)


class ProfileFollowSerializer(serializers.Serializer):
    """Follow serializer.
    
    Validates if the given user exists and 
    establishes a relationship between it
    and the request user.
    """

    pk = serializers.IntegerField()

    request_user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_pk(self, value):
        """Verify the followed user exists."""
        self.context['followed_user'] = get_object_or_404(
            User, pk=value, is_verified=True, is_client=True
        )
        return value

    def validate(self, data):
        """Verify the followed user
        is not the request user.
        """
        if self.context['followed_user'] == data['request_user']:
            raise serializers.ValidationError("A user cannot follow itself.")
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
