"""User Managers."""

# Django
from django.db.models import Manager
from django.http import Http406


class UserCustomManager(Manager):
    """User Custom Manager.
    
    UserCustomManager adds a method to update
    'followers' and 'following' attributes
    of the two related users.
    """

    def start_follow(self, current_user, followed_user):
        """Updates 'following' and 'followers' attributes
        of the current user and the followed user.
        """
        if current_user.pk == followed_user.pk:
            raise Http406('An user cannot follow itself.')

        current_user.profile.following.add(followed_user)
        current_user.profile.update_following()
                
        followed_user.profile.followers.add(current_user)
        followed_user.profile.update_followers()