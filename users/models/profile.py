"""Profile model."""

# REST Framework
from rest_framework.serializers import ValidationError as SerializerValidationError

# Django
from django.contrib.auth.models import User
from django.db import models

# Utils
from utils.models import AskalleryModel


class Profile(AskalleryModel, models.Model):
    """Profile model.
    
    A Profile holds the user's public data like biography, picture,
    and statistics.
    """

    user = models.OneToOneField('users.User', on_delete=models.CASCADE)

    picture = models.ImageField(
        'picture',
        upload_to='users/pictures/',
        blank=True,
        null=True,
        help_text='User profile picture.'
    )

    biography = models.TextField(
        'biography',
        null=True,
        blank=True,
        max_length=250,
        help_text='User profile biography.'
    )

    followers = models.ManyToManyField('users.User', related_name='followers')

    following = models.ManyToManyField('users.User', related_name='following')

    followers_quantity = models.IntegerField(
        'quantity of followers',
        default=0,
        help_text=(
            'Quantity of followers of this user.'
            'Stores the value to perform less queries.'
            'Increase 1 when another user begins to follow this user.',
        )
    )

    following_quantity = models.IntegerField(
        'quantity of following',
        default=0,
        help_text=(
            'Quantity of users that this user is following.',
            'Stores the value to perform less queries.'
            'Increase 1 when this user begins to follow another user.',
        )
    )

    def start_follow(self, followed_user):
        """Establishes a relationship between this user and passed user,
        also updates their 'following' and 'followers' attributes.
        """
        if self.user.pk == followed_user.pk:
            raise SerializerValidationError('An user cannot follow itself.')

        self.following.add(followed_user)
        self.following_quantity = self.following.count()
        self.save()
                
        followed_user.profile.followers.add(self.user)
        followed_user.profile.followers_quantity = followed_user.profile.followers.count()
        followed_user.save()

    def stop_following(self, followed_user):
        """Removes a relationship between this user and passed user,
        also updates their 'following' and 'followers' attributes.
        """
        if self.user.pk == followed_user.pk:
            raise SerializerValidationError('An user cannot follow itself.')

        self.following.remove(followed_user)
        self.following_quantity = self.following.count()
        self.save()
                
        followed_user.profile.followers.remove(self.user)
        followed_user.profile.followers_quantity = followed_user.profile.followers.count()
        followed_user.save()

    def __str__(self):
        """Retuens username."""
        return self.user.username