"""User serializers."""

# Django
from django.contrib.auth import password_validation, authenticate

# REST Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Serializers
from users.serializers import ProfileModelSerializer

# Models
from users.models import User, Profile


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    profile = ProfileModelSerializer(read_only=True)

    class Meta:
        """Meta options."""
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'profile',
        )


class MinimumUserFieldsModelSerializer(serializers.ModelSerializer):
    """Returns the minimum fields for be displayed in a front-end."""

    picture = serializers.SerializerMethodField()

    class Meta:
        """Meta options."""
        model = User
        fields = ('pk', 'username', 'picture')

    def get_picture(self, instance):
        """Returns user's profile picture."""
        if instance.profile.picture:
            return instance.profile.picture
        return None

class UserSignUpSerializer(serializers.Serializer):
    """User sign up serializer."""

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        min_length=8,
        max_length=64,
    )

    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    def validate(self, data):
        """Verifies passwords match."""
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError("Passwords don't match.")
        password_validation.validate_password(passwd)
        return data

    def create(self, data):
        """Handles user and profile creation."""
        data.pop('password_confirmation')
        user = User.objects.create_user(
            **data, 
            is_verified=False, 
            is_client=True,
        )
        Profile.objects.create(user=user)
        #send_confirmation_email()
        return user
