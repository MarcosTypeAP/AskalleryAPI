"""User serializers."""

# Django
from django.contrib.auth import password_validation
from django.conf import settings

# REST Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Serializers
from users.serializers import ProfileModelSerializer

# Models
from users.models import User, Profile

# Utils
from utils.serializers import send_confirmation_email
import jwt


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer."""

    profile = ProfileModelSerializer(read_only=True)

    class Meta:
        """Meta options."""
        model = User
        fields = (
            'pk', 'username', 'first_name',
            'last_name', 'profile'
        )


class MinimumUserFieldsModelSerializer(serializers.ModelSerializer):
    """Returns the minimum fields for be displayed in a front-end."""

    picture = serializers.SerializerMethodField()

    class Meta:
        """Meta options."""
        model = User
        fields = ('pk', 'first_name', 'last_name', 'username', 'picture')

    def get_picture(self, instance):
        """Returns user's profile picture."""
        if instance.profile.picture:
            request = self.context.get("request")
            return request.build_absolute_uri(instance.profile.picture.url)
        return None


class UserSignUpModelSerializer(serializers.ModelSerializer):
    """User sign up model serializer."""

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        min_length=8, max_length=64,
        write_only=True
    )

    password_confirmation = serializers.CharField(
        min_length=8, max_length=64,
        write_only=True
    )

    first_name = serializers.CharField(min_length=2, max_length=30)
    last_name = serializers.CharField(min_length=2, max_length=30)

    class Meta:
        """Meta options."""
        model = User
        fields = (
            'pk', 'email', 'first_name', 'last_name',
            'username', 'password', 'password_confirmation'
        )

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
        send_confirmation_email(user=user)
        return user


class AccountVerificationSerializer(serializers.Serializer):
    """Account verification serializer."""

    token = serializers.CharField(max_length=500)

    def validate_token(self, value):
        """Verifies that the token is valid."""
        try:
            payload = jwt.decode(
                value, settings.SECRET_KEY, algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired.')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')
        if payload['type'] != 'email_confirmation':
            raise serializers.ValidationError('Invalid token')

        self.context['payload'] = payload
        return value

    def save(self):
        """Update user's verified status."""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        user.is_verified = True
        user.save()
