"""User model."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser

# Utils
from utils.models import AskalleryModel


class User(AskalleryModel, AbstractUser):
    """User model.
    
    Extends from Django's Abstract User, changes the username field
    to email and overwrites it.
    """

    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with that email address already exists.'
        }
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_client = models.BooleanField(
        'client',
        default=True,
        help_text=(
            'Helps easily distinguish users and perform queries.',
            'Clients are the main type of user.'
        )
    )

    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='Set to True when the user has verified their email address.'
    )

    def __str__(self):
        """Returns username."""
        return self.username

    def get_short_name(self):
        """Returns username."""
        return self.username